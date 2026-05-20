import re

file_path = "axis_saas/public_urls.py"

with open(file_path, 'r') as f:
    content = f.read()

# Add correct import if missing
if "from django.db.models import Q" not in content:
    # Add after existing imports (e.g., after from django_tenants.utils import schema_context)
    content = content.replace(
        "from django_tenants.utils import schema_context",
        "from django.db.models import Q\nfrom django_tenants.utils import schema_context"
    )
    print("✅ Added import: from django.db.models import Q")

# Replace any occurrence of 'models.Q' with just 'Q'
content = content.replace("models.Q(", "Q(")
print("✅ Replaced models.Q( with Q(")

# Also ensure the function doesn't have any other issues (like missing Q variable)
# Write back
with open(file_path, 'w') as f:
    f.write(content)

print("✅ Fix applied. Restart server now.")
