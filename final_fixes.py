import re

# 1. Fix forms.py: add SchoolFeeSettings import
forms_path = "axis_saas/forms.py"
with open(forms_path, 'r') as f:
    forms_content = f.read()

old_import = "from .models import FeeRecord, PaymentTransaction, FeeStructure, Student"
new_import = "from .models import FeeRecord, PaymentTransaction, FeeStructure, Student, SchoolFeeSettings"
if old_import in forms_content:
    forms_content = forms_content.replace(old_import, new_import)
    with open(forms_path, 'w') as f:
        f.write(forms_content)
    print("✅ Added SchoolFeeSettings import to forms.py")
else:
    print("⚠️ Could not find the import line; manually check forms.py")

# 2. Fix student_profile.html: move fee history inside body block
profile_path = "templates/tenant/student_profile.html"
with open(profile_path, 'r') as f:
    profile = f.read()

# Replace the entire file with a corrected version
corrected_profile = """{% load fee_extras %}
{% extends 'tenant/base.html' %}

{% block title %}{{ tenant.name }} | Student Profile{% endblock %}

{% block sidebar_meta %}Student Profile{% endblock %}
{% block nav_students_active %}active{% endblock %}

{% block body %}
<div class="page-card">
    <div class="page-head" style="margin-bottom: 20px;">
        <div>
            <h1 class="page-title">Student Profile</h1>
            <p class="page-description">Complete details of {{ student.name }}</p>
        </div>
        <div>
            <a href="{% url 'school_portal_students' schema_name=tenant.schema_name %}" style="background: var(--surface-alt); padding: 8px 16px; border-radius: 6px; text-decoration: none;">← Back to List</a>
        </div>
    </div>

    <div style="background: var(--surface-alt); border-radius: 12px; padding: 24px;">
        <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px 30px;">
            <div><strong>Roll Number:</strong><br><span>{{ student.roll_number|default:"N/A" }}</span></div>
            <div><strong>Full Name:</strong><br><span>{{ student.name }}</span></div>
            <div><strong>Father's Name:</strong><br><span>{{ student.father_name }}</span></div>
            <div><strong>Father CNIC:</strong><br><span>{{ student.father_cnic }}</span></div>
            <div><strong>Parent Mobile:</strong><br><span>{{ student.parent_mobile }}</span></div>
            <div><strong>Class:</strong><br><span>{{ student.grade }}</span></div>
            <div><strong>Section:</strong><br><span>{{ student.section }}</span></div>
            <div><strong>Admission Date:</strong><br><span>{{ student.admission_date|date:"Y-m-d" }}</span></div>
            <div><strong>Status:</strong><br><span>{{ student.get_status_display }}</span></div>
            <div><strong>Gender:</strong><br><span>{{ student.get_gender_display|default:"Not specified" }}</span></div>
            <div><strong>Date of Birth:</strong><br><span>{{ student.date_of_birth|date:"Y-m-d"|default:"N/A" }}</span></div>
            <div><strong>Custom Fee:</strong><br><span>Rs. {{ student.custom_fee }}</span></div>
            <div><strong>Enrolled On:</strong><br><span>{{ student.enrolled_on|date:"Y-m-d H:i" }}</span></div>
            <div><strong>Address:</strong><br><span>{{ student.address|linebreaks|default:"N/A" }}</span></div>
            <div><strong>Notes:</strong><br><span>{{ student.notes|linebreaks|default:"N/A" }}</span></div>
        </div>
    </div>

    <div class="page-card" style="margin-top: 30px;">
        <h3>Fee History & Analytics</h3>
        <div style="display: flex; gap: 20px; margin-bottom: 20px;">
            <div class="stat-card"><span class="stat-label">Total Fee</span><p class="stat-value">Rs {{ student.fee_records.all|sum_attribute:'amount'|default:0 }}</p></div>
            <div class="stat-card"><span class="stat-label">Total Paid</span><p class="stat-value">Rs {{ student.payments.all|sum_attribute:'amount'|default:0 }}</p></div>
            <div class="stat-card"><span class="stat-label">Pending</span><p class="stat-value">Rs {{ student.fee_records.all|sum_remaining|default:0 }}</p></div>
        </div>
        <table style="width:100%">
            <tr><th>Month/Year</th><th>Amount</th><th>Paid</th><th>Status</th><th>Receipt</th></tr>
            {% for fr in student.fee_records.all %}
            <tr>
                <td>{{ fr.month }}/{{ fr.year }}</td>
                <td>Rs {{ fr.amount }}</td>
                <td>Rs {{ fr.paid_amount }}</td>
                <td>{{ fr.get_status_display }}</td>
                <td>
                    {% for pay in fr.payments.all %}
                    <a href="{% url 'fee_receipt' schema_name=tenant.schema_name receipt_id=pay.id %}" target="_blank">Receipt {{ pay.receipt_number }}</a><br>
                    {% empty %}—{% endfor %}
                </td>
            </tr>
            {% empty %}<tr><td colspan="5">No fee records found.</td></tr>{% endfor %}
        </table>
    </div>
</div>
{% endblock %}"""

with open(profile_path, 'w') as f:
    f.write(corrected_profile)
print("✅ Fixed student_profile.html (fee history inside block)")

print("\n✅ All fixes applied. Restart server:")
print("   python manage.py runserver")
