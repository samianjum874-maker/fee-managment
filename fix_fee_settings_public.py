import re

FILE = "axis_saas/public_urls.py"

with open(FILE, "r") as f:
    content = f.read()

# Fix fee_settings view: move get_or_create out of schema_context
old_fee_settings = '''@tenant_login_required
def fee_settings(request, schema_name, tenant=None):
    with schema_context(tenant.schema_name):
        settings_obj, created = SchoolFeeSettings.objects.get_or_create(tenant=tenant)
        if request.method == 'POST':
            form = FeeSettingsForm(request.POST, instance=settings_obj)
            if form.is_valid():
                form.save()
                messages.success(request, 'Fee settings updated successfully')
                return redirect('fee_settings', schema_name=tenant.schema_name)
        else:
            form = FeeSettingsForm(instance=settings_obj)
    logo_url = tenant.school_logo.url if tenant.school_logo else None
    return render(request, 'tenant/fee_settings.html', {'tenant': tenant, 'form': form, 'logo_url': logo_url})'''

new_fee_settings = '''@tenant_login_required
def fee_settings(request, schema_name, tenant=None):
    # SchoolFeeSettings lives in public schema (shared), so query outside tenant schema
    from django_tenants.utils import schema_context
    with schema_context('public'):
        settings_obj, created = SchoolFeeSettings.objects.get_or_create(tenant=tenant)
    with schema_context(tenant.schema_name):
        if request.method == 'POST':
            form = FeeSettingsForm(request.POST, instance=settings_obj)
            if form.is_valid():
                form.save()
                messages.success(request, 'Fee settings updated successfully')
                return redirect('fee_settings', schema_name=tenant.schema_name)
        else:
            form = FeeSettingsForm(instance=settings_obj)
    logo_url = tenant.school_logo.url if tenant.school_logo else None
    return render(request, 'tenant/fee_settings.html', {'tenant': tenant, 'form': form, 'logo_url': logo_url})'''

if old_fee_settings in content:
    content = content.replace(old_fee_settings, new_fee_settings)
    print("✅ Fixed fee_settings view (public schema get_or_create)")
else:
    # Fallback: find and replace manually
    print("⚠️ Could not find exact block, trying regex")
    pattern = r'def fee_settings\(request, schema_name, tenant=None\):.*?return render\(.*?\)'
    content = re.sub(pattern, new_fee_settings, content, flags=re.DOTALL)
    print("✅ Replaced using regex")

# Also fix fee_generate view similarly
old_fee_generate = '''@tenant_login_required
def fee_generate(request, schema_name, tenant=None):
    if request.method == 'POST':
        form = FeeGenerationForm(request.POST)
        if form.is_valid():
            month = form.cleaned_data['month']
            year = form.cleaned_data['year']
            generate_all = form.cleaned_data['generate_for_all']
            with schema_context(tenant.schema_name):
                students = Student.objects.filter(status='active')
                if not generate_all:
                    existing = FeeRecord.objects.filter(month=month, year=year).values_list('student_id', flat=True)
                    students = students.exclude(id__in=existing)
                fee_settings, _ = SchoolFeeSettings.objects.get_or_create(tenant=tenant)
                # ... rest unchanged ...'''

# We'll replace just the line where fee_settings is fetched
# Simpler: patch the line inside fee_generate where get_or_create is called.
pattern_fee_settings_in_generate = r'fee_settings, _ = SchoolFeeSettings.objects.get_or_create\(tenant=tenant\)'
replacement = 'with schema_context(\'public\'):\n                fee_settings, _ = SchoolFeeSettings.objects.get_or_create(tenant=tenant)'
if re.search(pattern_fee_settings_in_generate, content):
    content = re.sub(pattern_fee_settings_in_generate, replacement, content)
    print("✅ Fixed fee_generate view (public schema for fee_settings)")
else:
    print("⚠️ Could not find fee_settings get_or_create in fee_generate")

# Also need to import schema_context inside the function if not already available, but we already have it globally.

with open(FILE, "w") as f:
    f.write(content)

print("\n✅ Fix applied. Restart server: python manage.py runserver")
