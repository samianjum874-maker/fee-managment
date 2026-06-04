from django.core.management.base import BaseCommand
from django_tenants.utils import schema_context
from axis_saas.models import SchoolClient, GymCustomer, GymSubscription, GymSettings
from datetime import date, timedelta

class Command(BaseCommand):
    help = 'Generate monthly subscriptions for all active gym customers'

    def handle(self, *args, **options):
        tenants = SchoolClient.objects.filter(is_active=True, tenant_type='gym').exclude(schema_name='public')
        today = date.today()
        generated_total = 0
        for tenant in tenants:
            with schema_context(tenant.schema_name):
                settings, _ = GymSettings.objects.get_or_create(pk=1)
                if today.day == settings.subscription_generation_day:
                    month = today.month
                    year = today.year
                    if GymSubscription.objects.filter(month=month, year=year).exists():
                        self.stdout.write(f"{tenant.schema_name}: subscriptions already exist for {month}/{year}")
                        continue
                    due_date = today + timedelta(days=settings.due_date_offset)
                    customers = GymCustomer.objects.filter(status='active')
                    created = 0
                    for cust in customers:
                        fee = cust.monthly_fee if cust.monthly_fee > 0 else settings.default_monthly_fee
                        if fee > 0:
                            GymSubscription.objects.create(
                                customer=cust, month=month, year=year,
                                amount=fee, due_date=due_date, status='pending'
                            )
                            created += 1
                    self.stdout.write(f"{tenant.schema_name}: generated {created} subscriptions for {month}/{year}")
                    generated_total += created
                else:
                    self.stdout.write(f"{tenant.schema_name}: generation day {settings.subscription_generation_day} not today")
        self.stdout.write(self.style.SUCCESS(f"Total generated: {generated_total}"))
