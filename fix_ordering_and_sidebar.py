#!/usr/bin/env python3
import re

# ----------------------------------------------------------------------
# 1. Fix public_urls.py: move fee views before urlpatterns
# ----------------------------------------------------------------------
FILE = "axis_saas/public_urls.py"

with open(FILE, "r") as f:
    content = f.read()

# Find the start of fee views block (the one after the main views)
# It begins with "# ----------------------------------------------------------------------"
# and "# FEE MANAGEMENT VIEWS" comment, and ends right before "urlpatterns = ["
# We'll extract that block and place it after the student_profile function (before urlpatterns)

# First, locate the start of fee views block (look for "# FEE MANAGEMENT VIEWS")
fee_start = content.find("# FEE MANAGEMENT VIEWS")
if fee_start == -1:
    print("Could not find fee views block, exiting")
    exit(1)

# Find the end of the fee views block (just before "urlpatterns = [")
urlpatterns_pos = content.find("urlpatterns = [", fee_start)
if urlpatterns_pos == -1:
    print("Could not find urlpatterns block")
    exit(1)

# Extract the fee views block
fee_block = content[fee_start:urlpatterns_pos].rstrip()

# Now find the position where we want to insert it: after the student_profile function, before urlpatterns
# The student_profile function is defined earlier.
student_profile_end = content.find("@tenant_login_required\ndef student_profile", 0)
if student_profile_end == -1:
    # fallback: after the last non-fee view
    student_profile_end = content.rfind("def student_profile", 0, fee_start)
if student_profile_end == -1:
    print("Could not find student_profile, fallback to before urlpatterns")
    insert_pos = urlpatterns_pos
else:
    # find the end of the student_profile function (the line before next decorator or before urlpatterns)
    # We'll find the line after the return of student_profile
    lines = content[student_profile_end:urlpatterns_pos].splitlines()
    # find the line that contains "return render" and then the next line is blank or we just take the line index
    # simpler: insert just before urlpatterns
    insert_pos = urlpatterns_pos

# Remove the original fee block from its location (so we don't duplicate)
content = content[:fee_start] + content[urlpatterns_pos:]

# Insert the fee block at the new position (right before urlpatterns)
content = content[:insert_pos] + "\n\n" + fee_block + "\n\n" + content[insert_pos:]

# Also ensure all necessary imports are present (they already are, but just in case)
with open(FILE, "w") as f:
    f.write(content)

print("✅ Reordered public_urls.py: fee views now defined before urlpatterns")

# ----------------------------------------------------------------------
# 2. Fix base.html sidebar – remove duplicates and create clean menu
# ----------------------------------------------------------------------
BASE = "templates/tenant/base.html"

with open(BASE, "r") as f:
    sidebar = f.read()

# Find the navigation section (between <nav class="sidebar-nav"> and </nav>)
nav_start = sidebar.find('<nav class="sidebar-nav">')
nav_end = sidebar.find('</nav>', nav_start)
if nav_start == -1 or nav_end == -1:
    print("Could not find sidebar nav, skipping base.html fix")
else:
    # Define clean nav items
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

    # Replace the old nav block with clean one (keeping the rest of the file unchanged)
    sidebar = sidebar[:nav_start] + clean_nav + sidebar[nav_end+6:]  # +6 to include the closing </nav>

    # Also ensure the page-body messages inclusion is present (it is)
    with open(BASE, "w") as f:
        f.write(sidebar)

    print("✅ Cleaned up base.html sidebar (removed duplicates)")

print("\n✅ Fixes applied. Restart server now:\n   python manage.py runserver")
