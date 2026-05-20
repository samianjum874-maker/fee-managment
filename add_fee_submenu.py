import re

BASE_FILE = "templates/tenant/base.html"

with open(BASE_FILE, "r") as f:
    content = f.read()

# Find the "Fee Management" <a> tag and replace it with a dropdown structure
old_fee_link = '''                <a href="{% url 'fee_structure' schema_name=tenant.schema_name %}" class="{% block nav_fee_active %}{% endblock %}">
                    <svg width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" d="M12 6v12m-6-6h12"/></svg>
                    <span class="nav-label">Fee Management</span>
                </a>'''

new_dropdown = '''                <div class="dropdown">
                    <a href="#" class="dropdown-toggle" onclick="toggleFeeMenu()">
                        <svg width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" d="M12 6v12m-6-6h12"/></svg>
                        <span class="nav-label">Fee Management</span>
                        <svg width="12" height="12" style="margin-left:auto;" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" d="M19 9l-7 7-7-7"/>
                        </svg>
                    </a>
                    <div class="dropdown-menu" id="feeDropdown">
                        <a href="{% url 'fee_structure' schema_name=tenant.schema_name %}">📊 Fee Structure</a>
                        <a href="{% url 'fee_generate' schema_name=tenant.schema_name %}">⚙️ Generate Fees</a>
                        <a href="{% url 'pending_fees' schema_name=tenant.schema_name %}">⏳ Pending Fees</a>
                        <a href="{% url 'payment_history' schema_name=tenant.schema_name %}">📜 Payment History</a>
                        <a href="{% url 'family_payment' schema_name=tenant.schema_name %}">👨‍👩‍👧 Family Payment</a>
                        <a href="{% url 'fee_settings' schema_name=tenant.schema_name %}">⚙️ Settings</a>
                    </div>
                </div>'''

if old_fee_link in content:
    content = content.replace(old_fee_link, new_dropdown)
    print("✅ Replaced fee link with dropdown submenu")
else:
    print("⚠️ Could not find original fee link – trying regex")
    # Fallback: use regex to replace
    pattern = r'<a href="{% url \'fee_structure\'.*?</a>'
    content = re.sub(pattern, new_dropdown, content, flags=re.DOTALL)
    print("✅ Replaced using regex")

# Add CSS and JavaScript for the dropdown if not already present
if '<style>' in content and 'dropdown' not in content:
    # Inject CSS for dropdown before </style>
    dropdown_css = '''
        /* Dropdown menu styling */
        .dropdown { position: relative; }
        .dropdown-toggle { cursor: pointer; display: flex; align-items: center; gap: 12px; padding: 10px 12px; border-radius: 8px; color: var(--text); font-size: 0.92rem; font-weight: 500; transition: background 0.15s; }
        .dropdown-toggle:hover { background: var(--surface-alt); }
        .dropdown-menu {
            display: none;
            position: absolute;
            left: 0;
            top: 100%;
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 8px;
            min-width: 200px;
            z-index: 1000;
            box-shadow: var(--shadow);
            padding: 8px 0;
        }
        .dropdown-menu a {
            display: block;
            padding: 8px 16px;
            color: var(--text);
            text-decoration: none;
            font-size: 0.85rem;
            transition: background 0.15s;
        }
        .dropdown-menu a:hover { background: var(--surface-alt); }
        body.sidebar-collapsed .dropdown-menu { left: 100%; top: 0; margin-left: 8px; }
        body.sidebar-collapsed .dropdown-toggle svg:last-child { display: none; }
        body.sidebar-collapsed .dropdown { position: relative; }
    '''
    content = content.replace('</style>', dropdown_css + '\n    </style>')
    print("✅ Added dropdown CSS")

# Add JavaScript for toggle
if '<script>' in content and 'toggleFeeMenu' not in content:
    js_code = '''
        function toggleFeeMenu() {
            const menu = document.getElementById('feeDropdown');
            if (menu) {
                const isVisible = menu.style.display === 'block';
                menu.style.display = isVisible ? 'none' : 'block';
                // Close other dropdowns if any
            }
        }
        // Close dropdown when clicking outside
        document.addEventListener('click', function(event) {
            const dropdown = document.querySelector('.dropdown');
            const menu = document.getElementById('feeDropdown');
            if (dropdown && menu && !dropdown.contains(event.target)) {
                menu.style.display = 'none';
            }
        });
    '''
    # Insert before closing </script>
    content = content.replace('</script>', js_code + '\n    </script>')
    print("✅ Added dropdown JavaScript")

with open(BASE_FILE, "w") as f:
    f.write(content)

print("\n✅ Sidebar updated: Fee Management now has a dropdown submenu with all fee features.")
print("Restart server: python manage.py runserver")
