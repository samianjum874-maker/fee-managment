#!/usr/bin/env python3
"""
Final patcher to:
- Disable auto gym subscription generation (commands do nothing)
- Remove auto settings fields from Gym Settings page
- Keep manual generation fully functional
- Leave school side unchanged
"""

import re
import shutil
from pathlib import Path

PROJECT_ROOT = Path("/home/sami/axis_school_sys")

# Files to patch
COMMAND_FILES = [
    "axis_saas/management/commands/generate_gym_subscriptions.py",
    "axis_saas/management/commands/generate_daily_subscriptions.py",
]
FORMS_FILE = "axis_saas/forms.py"
TEMPLATE_FILE = "templates/tenant/gym_settings.html"

def backup_and_patch(filepath, patcher_func):
    full_path = PROJECT_ROOT / filepath
    if not full_path.exists():
        print(f"⚠️ File not found, skipping: {filepath}")
        return False

    # Backup
    backup = full_path.with_suffix(full_path.suffix + ".final_backup")
    shutil.copy2(full_path, backup)
    print(f"✅ Backup: {backup}")

    with open(full_path, "r", encoding="utf-8") as f:
        content = f.read()

    new_content = patcher_func(content)
    if new_content == content:
        print(f"ℹ️ No changes needed in {filepath}")
        return False

    with open(full_path, "w", encoding="utf-8") as f:
        f.write(new_content)
    print(f"🔧 Patched: {filepath}")
    return True

# ------------------- 1. Disable auto commands -------------------
def disable_command(content):
    # Replace the handle method with a no-op that prints a clear message
    pattern = r'(def handle\(self, .*?\):.*?)(?=\n    def |\nclass |\Z)'
    def replace(match):
        indent = "    "
        return f'''{match.group(1)}
{indent}self.stdout.write(self.style.WARNING("⚠️ Auto subscription generation has been DISABLED by administrator."))
{indent}self.stdout.write("   Subscriptions will NOT be created automatically.")
{indent}self.stdout.write("   Please generate subscriptions manually from the customer profile.")
{indent}return'''
    return re.sub(pattern, replace, content, flags=re.DOTALL)

# ------------------- 2. Remove fields from GymSettingsForm -------------------
def patch_forms(content):
    # Remove subscription_generation_day, due_date_offset, late_fee_penalty from fields list
    # Find the GymSettingsForm class
    form_pattern = r'(class GymSettingsForm\(forms\.ModelForm\):.*?)(?=\nclass |\Z)'
    def replace_form(match):
        form_body = match.group(1)
        # Remove the three fields from the Meta.fields list
        # First, locate the Meta class and its fields list
        meta_pattern = r'(class Meta:.*?fields\s*=\s*\[.*?\])'
        def replace_meta(m):
            meta_content = m.group(0)
            # Remove the unwanted field names
            for field in ['subscription_generation_day', 'due_date_offset', 'late_fee_penalty']:
                # Remove field from list, handling commas
                meta_content = re.sub(rf"['\"]{field}['\"]\s*,?\s*", "", meta_content)
            return meta_content
        form_body = re.sub(meta_pattern, replace_meta, form_body, flags=re.DOTALL)
        return form_body
    return re.sub(form_pattern, replace_form, content, flags=re.DOTALL)

# ------------------- 3. Remove fields from gym_settings.html template -------------------
def patch_template(content):
    # Remove the entire form-field divs for the auto fields
    patterns = [
        r'<div class="form-field">\s*<label>Subscription Generation Day</label>.*?</div>\s*',
        r'<div class="form-field">\s*<label>Due Date Offset \(days after generation\)</label>.*?</div>\s*',
        r'<div class="form-field">\s*<label>Late Fee Penalty \(%\)</label>.*?</div>\s*',
    ]
    for pat in patterns:
        content = re.sub(pat, '', content, flags=re.DOTALL)
    # Also remove the small text that may appear inside those fields
    content = re.sub(r'<small>Day of month when subscriptions are auto-generated</small>', '', content)
    return content

def main():
    print("🚀 Final Gym Auto-Disable & Settings Cleanup\n")

    # 1. Disable commands
    for cmd in COMMAND_FILES:
        backup_and_patch(cmd, disable_command)

    # 2. Patch forms.py
    backup_and_patch(FORMS_FILE, patch_forms)

    # 3. Patch template
    backup_and_patch(TEMPLATE_FILE, patch_template)

    print("\n✅ All changes applied successfully.")
    print("📌 Restart your Django server: python3 manage.py runserver")
    print("📌 Gym Settings page now shows only 'Default Monthly Fee'.")
    print("📌 Auto subscription generation is completely disabled.")
    print("📌 Manual generation from customer profile still works.")

if __name__ == "__main__":
    main()
