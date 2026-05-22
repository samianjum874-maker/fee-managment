#!/bin/bash

echo "🔧 Applying final fixes for student profile..."

# ----------------------------------------------------------------------
# 1. Fix public_urls.py - clean version
# ----------------------------------------------------------------------
cat > axis_saas/public_urls.py << 'EOF'
from django.contrib import admin
from django.urls import path, re_path, include
from django.conf import settings as django_settings
from django.conf.urls.static import static
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404

from .models import SchoolClient
from .views import dashboard, student_list, student_profile, fee_collection, fee_receipt
from .views import defaulters, reports, settings, fee_structure, fee_settings, family_payment
from .views import student_search_api, add_student, edit_student, fee_status_api, manual_generate_api, manual_generate_single_api
from .views import student_fee_records_api, student_payments_api

def saas_homepage(request):
    return HttpResponse('''
    <h1>AXIS School Management System</h1>
    <p>Welcome to Multi-Tenant Platform</p>
    <p>Go to <a href="/admin/">Admin Panel</a> to manage schools</p>
    ''')

def school_login(request, schema_name):
    tenant = get_object_or_404(SchoolClient, schema_name=schema_name)
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        if username == tenant.admin_username and password == tenant.admin_password:
            request.session['school_admin_authenticated'] = True
            request.session['school_admin_schema'] = tenant.schema_name
            request.session['school_admin_username'] = username
            return redirect('dashboard', schema_name=tenant.schema_name)
        return render(request, 'tenant/login.html', {'tenant': tenant, 'error': 'Invalid credentials'})
    return render(request, 'tenant/login.html', {'tenant': tenant})

def school_logout(request, schema_name):
    request.session.flush()
    return redirect('school_login', schema_name=schema_name)

def login_required_for_schema(view_func):
    def wrapper(request, schema_name, *args, **kwargs):
        if not request.session.get('school_admin_authenticated') or request.session.get('school_admin_schema') != schema_name:
            return redirect('school_login', schema_name=schema_name)
        return view_func(request, schema_name, *args, **kwargs)
    return wrapper

# Wrapped views
dashboard_view = login_required_for_schema(dashboard)
student_list_view = login_required_for_schema(student_list)
student_profile_view = login_required_for_schema(student_profile)
fee_collection_view = login_required_for_schema(fee_collection)
fee_receipt_view = login_required_for_schema(fee_receipt)
defaulters_view = login_required_for_schema(defaulters)
reports_view = login_required_for_schema(reports)
settings_view = login_required_for_schema(settings)
fee_structure_view = login_required_for_schema(fee_structure)
fee_settings_view = login_required_for_schema(fee_settings)
family_payment_view = login_required_for_schema(family_payment)
student_search_api_view = login_required_for_schema(student_search_api)
add_student_view = login_required_for_schema(add_student)
edit_student_view = login_required_for_schema(edit_student)
student_fee_records_api_view = login_required_for_schema(student_fee_records_api)
student_payments_api_view = login_required_for_schema(student_payments_api)

urlpatterns = [
    path('', saas_homepage),
    path('admin/', admin.site.urls),
    path('api/fee-status/', fee_status_api, name='fee_status_api'),
    path('api/manual-generate/', manual_generate_api, name='manual_generate_api'),
    path('api/manual-generate-single/', manual_generate_single_api, name='manual_generate_single_api'),
    
    # Auth
    path('portal/<slug:schema_name>/login/', school_login, name='school_login'),
    path('portal/<slug:schema_name>/login/', school_login, name='tenant_login'),
    path('portal/<slug:schema_name>/logout/', school_logout, name='school_logout'),
    path('portal/<slug:schema_name>/logout/', school_logout, name='tenant_logout'),
    
    # Core - using the wrapped views
    path('portal/<slug:schema_name>/', dashboard_view, name='dashboard'),
    path('portal/<slug:schema_name>/students/', student_list_view, name='student_list'),
    path('portal/<slug:schema_name>/students/add/', add_student_view, name='add_student'),
    path('portal/<slug:schema_name>/students/edit/<int:student_id>/', edit_student_view, name='edit_student'),
    path('portal/<slug:schema_name>/students/<int:student_id>/', student_profile_view, name='student_profile'),
    
    # Fee collection
    re_path(r'^portal/(?P<schema_name>[a-zA-Z0-9_-]+)/fee/collection/(?:(?P<student_id>\d+)/)?$', fee_collection_view, name='fee_collection'),
    
    path('portal/<slug:schema_name>/fee/receipt/<int:receipt_id>/', fee_receipt_view, name='fee_receipt'),
    path('portal/<slug:schema_name>/defaulters/', defaulters_view, name='defaulters'),
    path('portal/<slug:schema_name>/reports/', reports_view, name='reports'),
    path('portal/<slug:schema_name>/settings/', settings_view, name='settings'),
    path('portal/<slug:schema_name>/fee/structure/', fee_structure_view, name='fee_structure'),
    path('portal/<slug:schema_name>/fee/settings/', fee_settings_view, name='fee_settings'),
    path('portal/<slug:schema_name>/fee/family-payment/', family_payment_view, name='family_payment'),
    path('portal/<slug:schema_name>/api/student-search/', student_search_api_view, name='student_search_api'),
    path('portal/<slug:schema_name>/api/student/<int:student_id>/fee-records/', student_fee_records_api_view, name='student_fee_records_api'),
    path('portal/<slug:schema_name>/api/student/<int:student_id>/payments/', student_payments_api_view, name='student_payments_api'),
]

if django_settings.DEBUG:
    urlpatterns += static(django_settings.MEDIA_URL, document_root=django_settings.MEDIA_ROOT)
EOF

echo "✓ public_urls.py cleaned and fixed."

# ----------------------------------------------------------------------
# 2. Update views.py to include receipt_id in fee_records API
# ----------------------------------------------------------------------
if ! grep -q "'receipt_id'" axis_saas/views.py; then
    echo "➜ Updating student_fee_records_api to include receipt_id"
    sed -i '/def student_fee_records_api/,/return JsonResponse/ {
        s/'\''receipts'\'': \[p.receipt_number for p in r.payments.all()\]/'\''receipts'\'': [{"id": p.id, "number": p.receipt_number} for p in r.payments.all()]/
    }' axis_saas/views.py
fi

# ----------------------------------------------------------------------
# 3. Update student_profile.html to use receipt_id
# ----------------------------------------------------------------------
cat > templates/tenant/student_profile.html << 'HTML'
{% extends 'tenant/base.html' %}
{% block title %}{{ student.name }} | Profile{% endblock %}
{% block body %}
<div class="profile-header">
    <div>
        <h1 class="page-title">{{ student.name }}</h1>
        <p class="page-desc">Roll No: {{ student.roll_number }} • {{ student.grade }} - {{ student.section }}</p>
    </div>
    <div class="header-actions">
        <a href="{% url 'edit_student' schema_name=tenant.schema_name student_id=student.id %}" class="btn-secondary">✏️ Edit</a>
        <a href="{% url 'fee_collection' schema_name=tenant.schema_name %}?student_id={{ student.id }}" class="btn-primary">💰 Collect Fee</a>
        <a href="{% url 'student_list' schema_name=tenant.schema_name %}" class="btn-secondary">← Back</a>
    </div>
</div>

<div class="info-grid">
    <div class="info-card"><div class="info-label">Father Name</div><div class="info-value">{{ student.father_name }}</div></div>
    <div class="info-card"><div class="info-label">Father CNIC</div><div class="info-value">{{ student.father_cnic }}</div></div>
    <div class="info-card"><div class="info-label">Mobile</div><div class="info-value">{{ student.parent_mobile }}</div></div>
    <div class="info-card"><div class="info-label">Admission Date</div><div class="info-value">{{ student.admission_date|date:"Y-m-d" }}</div></div>
    <div class="info-card"><div class="info-label">Status</div><div class="info-value"><span class="status-badge status-{{ student.status }}">{{ student.get_status_display }}</span></div></div>
    <div class="info-card"><div class="info-label">Custom Fee</div><div class="info-value">₹{{ student.custom_fee }}</div></div>
</div>

<div class="fee-summary" id="feeSummary">
    <div class="summary-card"><div class="summary-label">Total Fee</div><div class="summary-value" id="totalFee">—</div></div>
    <div class="summary-card"><div class="summary-label">Total Paid</div><div class="summary-value" id="totalPaid">—</div></div>
    <div class="summary-card"><div class="summary-label">Pending</div><div class="summary-value pending" id="pendingTotal">—</div></div>
</div>

<div class="table-card">
    <div class="flex-header">
        <h3 class="section-title">📋 Fee History</h3>
        <button class="btn-generate-sm" id="genFeeForStudent" data-student-id="{{ student.id }}">Generate Current Month Fee</button>
    </div>
    <div class="table-responsive">
        <table class="data-table" id="feeTable">
            <thead><tr><th>Month/Year</th><th>Amount</th><th>Paid</th><th>Status</th><th>Receipt</th></tr></thead>
            <tbody id="feeTableBody"><tr><td colspan="5" class="loading-row">Loading...</td></tr></tbody>
        </table>
    </div>
</div>

<div class="table-card">
    <h3 class="section-title">💳 Payment History</h3>
    <div class="table-responsive">
        <table class="data-table" id="paymentTable">
            <thead><tr><th>Date</th><th>Amount</th><th>Mode</th><th>Receipt</th></td></thead>
            <tbody id="paymentTableBody"><tr><td colspan="4" class="loading-row">Loading...</td></tr></tbody>
        </table>
    </div>
</div>

<style>
.profile-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem; flex-wrap: wrap; gap: 1rem; }
.page-title { font-size: 1.8rem; font-weight: 700; background: linear-gradient(135deg, var(--primary), var(--primary-dark)); -webkit-background-clip: text; background-clip: text; color: transparent; }
.page-desc { color: var(--muted); }
.header-actions { display: flex; gap: 0.75rem; }
.btn-primary, .btn-secondary { display: inline-flex; align-items: center; gap: 0.5rem; padding: 0.5rem 1rem; border-radius: 2rem; font-weight: 500; font-size: 0.85rem; text-decoration: none; transition: all 0.2s; }
.btn-primary { background: var(--primary); color: white; }
.btn-secondary { background: var(--surface-alt); color: var(--text); border: 1px solid var(--border); }
.info-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 1rem; margin-bottom: 1.5rem; }
.info-card { background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius); padding: 1rem; }
.info-label { font-size: 0.75rem; text-transform: uppercase; color: var(--muted); letter-spacing: 0.5px; margin-bottom: 0.25rem; }
.info-value { font-weight: 600; font-size: 1rem; }
.fee-summary { display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; margin-bottom: 1.5rem; }
.summary-card { background: var(--surface); border-radius: var(--radius); padding: 1rem; text-align: center; border: 1px solid var(--border); }
.summary-label { font-size: 0.8rem; color: var(--muted); margin-bottom: 0.5rem; }
.summary-value { font-size: 1.6rem; font-weight: 700; color: var(--primary); }
.summary-value.pending { color: var(--danger); }
.table-card { background: var(--surface); border-radius: var(--radius); border: 1px solid var(--border); padding: 1rem; margin-bottom: 1.5rem; }
.flex-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; }
.section-title { font-size: 1.2rem; font-weight: 600; margin: 0; }
.btn-generate-sm { background: var(--primary); color: white; border: none; border-radius: 2rem; padding: 0.3rem 0.8rem; font-size: 0.7rem; cursor: pointer; }
.data-table { width: 100%; border-collapse: collapse; }
.data-table th, .data-table td { padding: 0.75rem; text-align: left; border-bottom: 1px solid var(--border); }
.data-table th { background: var(--surface-alt); font-weight: 600; font-size: 0.75rem; text-transform: uppercase; color: var(--muted); }
.status-badge { display: inline-block; padding: 0.2rem 0.6rem; border-radius: 2rem; font-size: 0.7rem; font-weight: 600; }
.status-pending { background: #fed7aa; color: #9a3412; }
.status-partial { background: #e0e7ff; color: #3730a3; }
.status-paid { background: #d1fae5; color: #065f46; }
.status-overdue { background: #fee2e2; color: #991b1b; }
.receipt-link { color: var(--primary); text-decoration: none; font-family: monospace; }
.loading-row { text-align: center; color: var(--muted); }
.empty-row { text-align: center; padding: 1rem; color: var(--muted); }
</style>

<script>
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
const csrfToken = getCookie('csrftoken');
const schema = '{{ tenant.schema_name }}';
const studentId = {{ student.id }};

async function loadFeeRecords() {
    try {
        const resp = await fetch(`/portal/${schema}/api/student/${studentId}/fee-records/`);
        const data = await resp.json();
        const tbody = document.getElementById('feeTableBody');
        if (data.length === 0) {
            tbody.innerHTML = '<tr><td colspan="5" class="empty-row">No fee records found. Click "Generate Current Month Fee" to create.</td></tr>';
            document.getElementById('totalFee').innerText = '₹0';
            document.getElementById('totalPaid').innerText = '₹0';
            document.getElementById('pendingTotal').innerText = '₹0';
            return;
        }
        let totalFee = 0, totalPaid = 0;
        let html = '';
        for (let r of data) {
            totalFee += r.amount;
            totalPaid += r.paid_amount;
            let receiptsHtml = '';
            if (r.receipts && r.receipts.length) {
                receiptsHtml = r.receipts.map(rc => `<a href="/portal/${schema}/fee/receipt/${rc.id}/" class="receipt-link">${rc.number}</a>`).join(', ');
            } else {
                receiptsHtml = '—';
            }
            html += `<tr>
                        <td>${r.month}/${r.year}</td>
                        <td>₹${r.amount.toFixed(2)}</td>
                        <td>₹${r.paid_amount.toFixed(2)}</td>
                        <td><span class="status-badge status-${r.status.toLowerCase()}">${r.status}</span></td>
                        <td>${receiptsHtml}</td>
                     </tr>`;
        }
        tbody.innerHTML = html;
        const pending = totalFee - totalPaid;
        document.getElementById('totalFee').innerHTML = `₹${totalFee.toFixed(2)}`;
        document.getElementById('totalPaid').innerHTML = `₹${totalPaid.toFixed(2)}`;
        const pendingSpan = document.getElementById('pendingTotal');
        pendingSpan.innerHTML = `₹${pending.toFixed(2)}`;
        if (pending > 0) pendingSpan.classList.add('pending');
        else pendingSpan.classList.remove('pending');
    } catch(e) {
        console.error('Fee load error:', e);
        document.getElementById('feeTableBody').innerHTML = '<tr><td colspan="5" class="empty-row">Error loading fee records. Backend error: ' + e.message + '</td></tr>';
    }
}

async function loadPayments() {
    try {
        const resp = await fetch(`/portal/${schema}/api/student/${studentId}/payments/`);
        const data = await resp.json();
        const tbody = document.getElementById('paymentTableBody');
        if (data.length === 0) {
            tbody.innerHTML = '<tr><td colspan="4" class="empty-row">No payments recorded yet.</td></tr>';
            return;
        }
        let html = '';
        for (let p of data) {
            html += `<tr>
                        <td>${p.date}</td>
                        <td>₹${p.amount.toFixed(2)}</td>
                        <td>${p.mode}</td>
                        <td><a href="${p.url}" class="receipt-link" target="_blank">${p.receipt_number}</a></td>
                     </tr>`;
        }
        tbody.innerHTML = html;
    } catch(e) {
        console.error('Payment load error:', e);
        document.getElementById('paymentTableBody').innerHTML = '<tr><td colspan="4" class="empty-row">Error loading payment history.后端错误: ' + e.message + '</td></tr>';
    }
}

async function generateFee() {
    const btn = document.getElementById('genFeeForStudent');
    if (!confirm('Generate current month fee for this student?')) return;
    btn.disabled = true;
    btn.innerText = 'Generating...';
    try {
        const resp = await fetch(`/api/manual-generate-single/?student_id=${studentId}`, {
            method: 'POST',
            headers: { 'X-CSRFToken': csrfToken, 'Content-Type': 'application/json' },
        });
        const data = await resp.json();
        alert(data.message || data.error);
        if (!data.error) {
            await loadFeeRecords();
            await loadPayments();
        }
    } catch(e) {
        alert('Error generating fee: ' + e.message);
    } finally {
        btn.disabled = false;
        btn.innerText = 'Generate Current Month Fee';
    }
}

document.getElementById('genFeeForStudent').addEventListener('click', generateFee);
loadFeeRecords();
loadPayments();
</script>
{% endblock %}
HTML

echo "✅ student_profile.html updated with receipt ID support."
echo "🔁 Restart your Django server and clear browser cache."
echo "📌 The student profile should now show correct data."
