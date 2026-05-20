from django import forms
from .models import FeeRecord, PaymentTransaction, FeeStructure, Student, SchoolFeeSettings, SchoolFeeSettings
from decimal import Decimal

class FeeStructureForm(forms.ModelForm):
    class Meta:
        model = FeeStructure
        fields = ['grade', 'monthly_fee']

class FeeGenerationForm(forms.Form):
    month = forms.ChoiceField(choices=[(i, i) for i in range(1,13)], label='Month')
    year = forms.IntegerField(min_value=2020, max_value=2030, initial=2026, label='Year')
    generate_for_all = forms.BooleanField(required=False, label='Generate for all active students (if unchecked, only for students without fee record for this month)')

class PaymentForm(forms.Form):
    student_id = forms.IntegerField(widget=forms.HiddenInput())
    amount = forms.DecimalField(max_digits=10, decimal_places=2)
    payment_mode = forms.ChoiceField(choices=PaymentTransaction.PAYMENT_MODE_CHOICES)
    remarks = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows': 2}))

class FamilyPaymentForm(forms.Form):
    father_cnic = forms.CharField(max_length=15, label="Father CNIC", required=True)
    amount = forms.DecimalField(max_digits=10, decimal_places=2, required=False, label="Amount to Pay (leave empty to pay all pending)")
    payment_mode = forms.ChoiceField(choices=PaymentTransaction.PAYMENT_MODE_CHOICES)
    remarks = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows': 2}))

class FeeSettingsForm(forms.ModelForm):
    class Meta:
        model = SchoolFeeSettings
        fields = ['fee_generation_day', 'due_date_offset', 'late_fee_penalty']
