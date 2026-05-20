#!/usr/bin/env python3
import re

# ----------------------------------------------------------------------
# 1. Reorder public_urls.py: move fee views before urlpatterns
# ----------------------------------------------------------------------
FILE = "axis_saas/public_urls.py"

with open(FILE, "r") as f:
    content = f.read()

# Locate the fee views block (starts with "# FEE MANAGEMENT VIEWS")
fee_start = content.find("# FEE MANAGEMENT VIEWS")
if fee_start == -1:
    print("ERROR: Could not find '# FEE MANAGEMENT VIEWS'")
    exit(1)

# Find the first occurrence of "urlpatterns = ["
urlpatterns_pos = content.find("urlpatterns = [")
if urlpatterns_pos == -1:
    print("ERROR: Could not find 'urlpatterns = ['")
    exit(1)

# Extract the fee views block (from fee_start up to urlpatterns_pos)
fee_block = content[fee_start:urlpatterns_pos].rstrip()

# Remove this block from its current location
content = content[:fee_start] + content[urlpatterns_pos:]

# Insert the fee block right before the first urlpatterns line (which now starts at the same index)
# We need to find the urlpatterns position again in the new content
new_urlpatterns_pos = content.find("urlpatterns = [")
if new_urlpatterns_pos == -1:
    print("ERROR: Could not find urlpatterns after removal")
    exit(1)

# Insert the fee block before that line
content = content[:new_urlpatterns_pos] + fee_block + "\n\n" + content[new_urlpatterns_pos:]

# Write back
with open(FILE, "w") as f:
    f.write(content)

print("✅ Reordered fee views before urlpatterns")

# ----------------------------------------------------------------------
# 2. Fix base.html sidebar (remove duplicates, clean menu)
# ----------------------------------------------------------------------
BASE = "templates/tenant/base.html"

with open(BASE, "r") as f:
    html = f.read()

# Define clean navigation block
clean_nav = '''            <nav class="sidebar-nav">
                <a href="{% url 'school_portal' schema_name=tenant.schema_name %}" class="{% block nav_dashboard_active %}{% endblock %}">
                    <svg width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" d="M2.25 12l8.954-8.955c.44-.439 1.152-.439 1.591 0L21.75 12M4.5 9.75v10.125c0 .621.504 1.125 1.125 1.125H9.75v-4.875c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125V21h4.125c.621 0 1.125-.504 1.125-1.125V9.75M8.25 21h8.25"/>
                    </svg>
                    <span class="nav-label">Dashboard</span>
                </a>
                <a href="{% url 'school_portal_students' schema_name=tenant.schema_name %}" class="{% block nav_students_active %}{% endblock %}">
                    <svg width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" d="M15.75 6a3.75 3.75 0 11-7.5 0 3.75 3.75 0 017.5 0zM4.501 20.118a7.5 7.5 0 0114.998 0A17.933 17.933 0 0112 21.75c-2.676 0-5.216-.584-7.499-1.632z"/>
                    </svg>
                    <span class="nav-label">Students</span>
                </a>
                <a href="{% url 'fee_structure' schema_name=tenant.schema_name %}" class="{% block nav_fee_active %}{% endblock %}">
                    <svg width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" d="M12 6v12m-6-6h12"/></svg>
                    <span class="nav-label">Fee Management</span>
                </a>
            </nav>'''

# Replace the existing nav block (from <nav class="sidebar-nav"> to </nav>)
pattern = r'<nav class="sidebar-nav">.*?</nav>'
html = re.sub(pattern, clean_nav, html, flags=re.DOTALL)

# Ensure messages inclusion is present (it should already be there, but just in case)
if '{% if messages %}' not in html:
    # Insert messages block after <main class="page-body"> if missing
    html = html.replace('<main class="page-body">', '<main class="page-body">\n            {% if messages %}\n                {% include "tenant/messages.html" %}\n            {% endif %}')

with open(BASE, "w") as f:
    f.write(html)

print("✅ Cleaned up base.html sidebar (single Fee Management link)")

print("\n✅ All fixes applied. Restart the server:")
print("   python manage.py runserver")
