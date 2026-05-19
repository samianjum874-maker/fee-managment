from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Student
from django import forms

class StudentAdmissionForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = [
            'name', 'father_name', 'father_cnic', 'parent_mobile', 
            'grade', 'section', 'admission_date', 'status',
            'gender', 'date_of_birth', 'address', 'notes'
        ]
        widgets = {
            'admission_date': forms.DateInput(attrs={'type': 'date'}),
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'address': forms.Textarea(attrs={'rows': 2}),
            'notes': forms.Textarea(attrs={'rows': 2}),
        }

@login_required
def tenant_dashboard(request):
    if request.tenant.schema_name == 'public':
        return redirect('/admin/')
    
    students = Student.objects.all().order_by('-enrolled_on')
    return render(request, 'tenant/dashboard.html', {'students': students})

@login_required
def add_student_instance(request):
    if request.tenant.schema_name == 'public':
        return redirect('/admin/')

    if request.method == 'POST':
        form = StudentAdmissionForm(request.POST)
        if form.is_valid():
            student = form.save(commit=False)
            # Automatic dynamic sequence token generation for strong isolation tracking
            total_students = Student.objects.count() + 1
            student.roll_number = f"AX-{request.tenant.schema_name.upper()}-{2026}-{total_students:04d}"
            student.save()
            messages.success(request, f"Student {student.name} securely provisioned into ledgers with Token: {student.roll_number}")
            return redirect('school_home')
    else:
        form = StudentAdmissionForm()
        
    return render(request, 'tenant/student_form.html', {'form': form})

from .models import FeeStructure

class FeeSetupForm(forms.ModelForm):
    class Meta:
        model = FeeStructure
        fields = ['grade', 'monthly_fee']

@login_required
def fee_management_dashboard(request):
    if request.tenant.schema_name == 'public':
        return redirect('/admin/')
    
    fee_structures = FeeStructure.objects.all().order_by('grade')
    
    if request.method == 'POST':
        form = FeeSetupForm(request.POST)
        if form.is_valid():
            grade_target = form.cleaned_data['grade']
            fee_amount = form.cleaned_data['monthly_fee']
            
            # Upsert operations
            fee_obj, created = FeeStructure.objects.update_or_create(
                grade=grade_target,
                defaults={'monthly_fee': fee_amount}
            )
            # Cascade safe runtime trigger manually for existing set
            Student.objects.filter(grade=grade_target).update(custom_fee=fee_amount)
            
            messages.success(request, f"Fee successfully updated for Class {grade_target} to RS {fee_amount}.")
            return redirect('fee_dashboard')
    else:
        form = FeeSetupForm()
        
    return render(request, 'tenant/fee_dashboard.html', {
        'fee_structures': fee_structures,
        'form': form
    })
