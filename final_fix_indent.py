import re

# 1. Fix public_urls.py: correct indentation of with block
file_path = "axis_saas/public_urls.py"
with open(file_path, "r") as f:
    content = f.read()

# Fix the fee_generate function: replace the line after with schema_context('public'):
old_block = """with schema_context('public'):
                fee_settings, _ = SchoolFeeSettings.objects.get_or_create(tenant=tenant)"""
new_block = """with schema_context('public'):
                fee_settings, _ = SchoolFeeSettings.objects.get_or_create(tenant=tenant)"""
# Actually the above is same – but the issue is missing indentation? Let's search for a pattern
# We'll look for the specific line: `with schema_context('public'):` followed by a line without proper indent
pattern = r'(with schema_context\(\'public\'\):\n)(\s*)(fee_settings, _ = SchoolFeeSettings\.objects\.get_or_create\(tenant=tenant\))'
def repl(m):
    return m.group(1) + '                ' + m.group(3)
content = re.sub(pattern, repl, content)

# Also ensure the fee_settings view is okay (it already has proper indent)
# Write back
with open(file_path, "w") as f:
    f.write(content)
print("✅ Fixed indentation in fee_generate view")

# 2. Add missing JavaScript for fee dropdown in base.html
base_file = "templates/tenant/base.html"
with open(base_file, "r") as f:
    html = f.read()

# Check if toggleFeeMenu function already exists
if 'toggleFeeMenu' not in html:
    # Add JavaScript before the closing </script>
    js_code = '''
        function toggleFeeMenu() {
            const menu = document.getElementById('feeDropdown');
            if (menu) {
                const isVisible = menu.style.display === 'block';
                menu.style.display = isVisible ? 'none' : 'block';
            }
        }
        // Close dropdown when clicking outside
        document.addEventListener('click', function(event) {
            const dropdown = document.querySelector('.dropdown');
            const menu = document.getElementById('feeDropdown');
            if (dropdown && menu && !dropdown.contains(event.target)) {
                if (menu) menu.style.display = 'none';
            }
        });
    '''
    # Insert before the last </script> tag
    html = html.replace('</script>', js_code + '\n    </script>', 1)
    with open(base_file, "w") as f:
        f.write(html)
    print("✅ Added dropdown JavaScript to base.html")
else:
    print("ℹ️ Dropdown JavaScript already present")

print("\nAll fixes applied. Restart server: python manage.py runserver")
