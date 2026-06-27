from datetime import date, datetime
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import patch
from django.test import SimpleTestCase

from axis_saas.fee_utils import calculate_fee_total, resolve_student_fee_plan, should_generate_on_date


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

    def test_should_generate_on_date_uses_last_day_for_short_months(self):
        self.assertTrue(should_generate_on_date(date(2024, 2, 29), 31))
        self.assertFalse(should_generate_on_date(date(2024, 2, 28), 31))

    @patch('axis_saas.models.FeeStructure')
    def test_resolve_student_fee_plan_prefers_grade_structure_over_student_custom_fee(self, fee_structure_cls):
        student = SimpleNamespace(grade='Grade 8', custom_fee=Decimal('2500'))
        fee_structure_cls.objects.filter.return_value.first.return_value = SimpleNamespace(monthly_fee=Decimal('1800'))

        base_fee, items, total_amount = resolve_student_fee_plan(student)

        self.assertEqual(base_fee, Decimal('1800'))
        self.assertEqual(items, [])
        self.assertEqual(total_amount, Decimal('1800'))
