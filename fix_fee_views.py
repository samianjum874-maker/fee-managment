import re

FILE = "axis_saas/public_urls.py"

with open(FILE, "r") as f:
    content = f.read()

# Find the fee views block start (the line with "# FEE MANAGEMENT VIEWS")
fee_start = content.find("# FEE MANAGEMENT VIEWS")
if fee_start == -1:
    print("Error: Could not find '# FEE MANAGEMENT VIEWS'")
    exit(1)

# Find the end of the fee views block: we need to locate the start of "urlpatterns = ["
urlpatterns_pos = content.find("urlpatterns = [")
if urlpatterns_pos == -1:
    print("Error: Could not find 'urlpatterns = ['")
    exit(1)

# The fee block ends right before the urlpatterns line (or possibly after it, but we'll cut from fee_start to urlpatterns_pos)
fee_block = content[fee_start:urlpatterns_pos].rstrip()

# Remove this block from the original content
content_without_fee = content[:fee_start] + content[urlpatterns_pos:]

# Now find the position where we want to insert the fee block: after the student_profile function and before urlpatterns.
# We need to locate the end of the student_profile function. Let's find the line where student_profile ends (the line before the next decorator or before urlpatterns).
# Since we removed the fee block, the new content has only the original views before urlpatterns.
# Let's find the index of "urlpatterns = [" in the new content
new_urlpatterns_pos = content_without_fee.find("urlpatterns = [")
if new_urlpatterns_pos == -1:
    print("Error: Could not find urlpatterns after removal")
    exit(1)

# Find the last occurrence of "def student_profile" in the new content (before urlpatterns)
# We'll look for "@tenant_login_required\ndef student_profile" and then find its end.
student_profile_start = content_without_fee.find("@tenant_login_required\ndef student_profile")
if student_profile_start == -1:
    # Fallback: just insert before urlpatterns
    insert_pos = new_urlpatterns_pos
else:
    # Find the end of the student_profile function (the next line that starts with 'def' or '@' or the line before urlpatterns)
    # Let's find the line after the function's last return. Simpler: use the position of the next '@tenant_login_required' or 'def ' after it.
    # We'll search from student_profile_start forward for the next occurrence of '@tenant_login_required' or 'def ' (excluding the one we just found)
    next_decorator_pos = content_without_fee.find("@tenant_login_required", student_profile_start + 1)
    next_def_pos = content_without_fee.find("\ndef ", student_profile_start + 1)
    # Find the smallest positive index after student_profile_start
    candidates = [p for p in [next_decorator_pos, next_def_pos] if p != -1 and p < new_urlpatterns_pos]
    if candidates:
        insert_pos = min(candidates)
    else:
        insert_pos = new_urlpatterns_pos

# Now insert the fee block at insert_pos
new_content = content_without_fee[:insert_pos] + "\n\n" + fee_block + "\n\n" + content_without_fee[insert_pos:]

# Write back
with open(FILE, "w") as f:
    f.write(new_content)

print("✅ Successfully moved fee views before urlpatterns")
