from django.core.management.base import BaseCommand
from django_tenants.utils import schema_context
from axis_saas.models import SchoolClient, SchoolFeeSettings, Student, FeeRecord
from axis_saas.fee_utils import resolve_student_fee_plan
from datetime import date, timedelta

class Command(BaseCommand):
    help = 'Automatically generate monthly fees for all tenants based on their generation day'

    def handle(self, *args, **options):
        tenants = SchoolClient.objects.filter(is_active=True).exclude(schema_name='public')
        today = date.today()
        for tenant in tenants:
            with schema_context(tenant.schema_name):
                settings, _ = SchoolFeeSettings.objects.get_or_create(pk=1)
                if today.day == settings.fee_generation_day:
                    month, year = today.month, today.year
                    due_date = today + timedelta(days=settings.due_date_offset)
                    students = Student.objects.filter(status='active')
                    created = 0
                    updated = 0
                    skipped = 0
                    for s in students:
                        existing = FeeRecord.objects.filter(student=s, month=month, year=year).first()
                        if existing and existing.paid_amount > 0:
                            skipped += 1
                            continue
                        try:
                            _, _, amount = resolve_student_fee_plan(s)
                        except ValueError:
                            skipped += 1
                            continue
                        if existing:
                            existing.amount = amount
                            existing.due_date = due_date
                            existing.remarks = ''
                            existing.save(update_fields=['amount', 'due_date', 'remarks'])
                            updated += 1
                        else:
                            FeeRecord.objects.create(student=s, month=month, year=year, amount=amount, due_date=due_date, status='pending')
                            created += 1
                    self.stdout.write(f"{tenant.schema_name}: generated {created} records, updated {updated} existing, skipped {skipped} for {month}/{year}")
                else:
                    self.stdout.write(f"{tenant.schema_name}: generation day {settings.fee_generation_day} not today")
