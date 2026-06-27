from decimal import Decimal
from types import SimpleNamespace
from django.test import SimpleTestCase

from axis_saas.fee_utils import calculate_fee_total, resolve_student_fee_plan


class FeeUtilsTests(SimpleTestCase):
    def test_calculate_fee_total_uses_base_fee_and_optional_items(self):
        total = calculate_fee_total(Decimal('1200.50'), [{'title': 'Security', 'amount': '100.00'}])
        self.assertEqual(total, Decimal('1300.50'))

    def test_calculate_fee_total_ignores_blank_items(self):
        total = calculate_fee_total(Decimal('500'), [{'title': '', 'amount': ''}, {'title': 'Lab', 'amount': '50.50'}])
        self.assertEqual(total, Decimal('550.50'))

    def test_resolve_student_fee_plan_uses_saved_items_when_present(self):
        student = SimpleNamespace(custom_fee=Decimal('1000'), fee_custom_items=[{'title': 'Security', 'amount': '50.00'}])
        base_fee, items, total_amount = resolve_student_fee_plan(student)
        self.assertEqual(base_fee, Decimal('1000'))
        self.assertEqual(items[0]['title'], 'Security')
        self.assertEqual(total_amount, Decimal('1050.00'))
