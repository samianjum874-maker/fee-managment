from django.core.management.base import BaseCommand
from django_tenants.utils import schema_context
from axis_saas.models import SchoolClient, SchoolFeeSettings, Student, FeeRecord
from axis_saas.fee_utils import resolve_student_fee_plan, should_generate_on_date
from datetime import date, timedelta


class Command(BaseCommand):
    help = 'Generate monthly fee records for all tenants based on their fee_generation_day'

    def handle(self, *args, **options):
        tenants = SchoolClient.objects.filter(is_active=True).exclude(schema_name='public')
        today = date.today()
        generated_count = 0

        for tenant in tenants:
            with schema_context(tenant.schema_name):
                settings, _ = SchoolFeeSettings.objects.get_or_create(pk=1)
                if not should_generate_on_date(today, settings.fee_generation_day):
                    self.stdout.write(f"Skipping {tenant.schema_name} - generation day mismatch")
                    continue

                month = today.month
                year = today.year
                students = Student.objects.filter(status='active')
                due_date = today + timedelta(days=settings.due_date_offset)
                created_records = 0
                updated_records = 0

                for student in students:
                    existing = FeeRecord.objects.filter(student=student, month=month, year=year).first()
                    if existing:
                        if existing.paid_amount > 0:
                            continue
                        try:
                            _, _, total_amount = resolve_student_fee_plan(student)
                        except ValueError:
                            continue
                        existing.amount = total_amount
                        existing.due_date = due_date
                        existing.remarks = ''
                        existing.save(update_fields=['amount', 'due_date', 'remarks'])
                        updated_records += 1
                        continue

                    try:
                        _, _, total_amount = resolve_student_fee_plan(student)
                    except ValueError:
                        continue
                    FeeRecord.objects.create(
                        student=student, month=month, year=year,
                        amount=total_amount, due_date=due_date, status='pending'
                    )
                    created_records += 1

                generated_count += created_records
                self.stdout.write(f"Generated {created_records} new fee records and updated {updated_records} existing unpaid vouchers for {tenant.schema_name}")

        self.stdout.write(self.style.SUCCESS(f"Total: {generated_count} new records"))
