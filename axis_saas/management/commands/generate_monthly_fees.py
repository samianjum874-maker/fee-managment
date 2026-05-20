from django.core.management.base import BaseCommand
from django.db import connection
from axis_saas.models import SchoolClient, SchoolFeeSettings, Student, FeeRecord, FeeStructure
from datetime import date, timedelta
from decimal import Decimal
from django_tenants.utils import schema_context

class Command(BaseCommand):
    help = 'Generate monthly fee records for all tenants based on their fee_generation_day'

    def handle(self, *args, **options):
        tenants = SchoolClient.objects.filter(is_active=True).exclude(schema_name='public')
        today = date.today()
        for tenant in tenants:
            with schema_context(tenant.schema_name):
                settings, _ = SchoolFeeSettings.objects.get_or_create(tenant=tenant)
                generation_day = settings.fee_generation_day
                # Check if today is generation day
                if today.day == generation_day:
                    # Determine month/year to generate (current month)
                    month = today.month
                    year = today.year
                    # Avoid generating twice
                    if FeeRecord.objects.filter(month=month, year=year).exists():
                        self.stdout.write(f"Skipping {tenant.schema_name} - fees already generated for {month}/{year}")
                        continue
                    students = Student.objects.filter(status='active')
                    # Due date calculation
                    if month == 12:
                        due_year = year + 1
                        due_month = 1
                    else:
                        due_year = year
                        due_month = month + 1
                    due_date = date(due_year, due_month, 1) + timedelta(days=settings.due_date_offset - 1)
                    created = 0
                    for student in students:
                        base_fee = student.custom_fee if student.custom_fee > 0 else (FeeStructure.objects.filter(grade=student.grade).first().monthly_fee if FeeStructure.objects.filter(grade=student.grade).exists() else 0)
                        if base_fee > 0:
                            FeeRecord.objects.get_or_create(
                                student=student,
                                month=month,
                                year=year,
                                defaults={
                                    'amount': base_fee,
                                    'due_date': due_date
                                }
                            )
                            created += 1
                    self.stdout.write(f"Generated {created} fee records for {tenant.schema_name} for {month}/{year}")
                else:
                    self.stdout.write(f"Skipping {tenant.schema_name} - generation day {generation_day} not today")
