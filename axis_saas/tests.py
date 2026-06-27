from decimal import Decimal
from django.test import SimpleTestCase

from axis_saas.fee_utils import calculate_fee_total


class FeeUtilsTests(SimpleTestCase):
    def test_calculate_fee_total_uses_base_fee_and_optional_items(self):
        total = calculate_fee_total(Decimal('1200.50'), [{'title': 'Security', 'amount': '100.00'}])
        self.assertEqual(total, Decimal('1300.50'))

    def test_calculate_fee_total_ignores_blank_items(self):
        total = calculate_fee_total(Decimal('500'), [{'title': '', 'amount': ''}, {'title': 'Lab', 'amount': '50.50'}])
        self.assertEqual(total, Decimal('550.50'))
