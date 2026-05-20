import re

file_path = "axis_saas/public_urls.py"

with open(file_path, "r") as f:
    lines = f.readlines()

# Find the line containing "with schema_context('public'):" and ensure the next line has proper indentation
new_lines = []
i = 0
while i < len(lines):
    line = lines[i]
    new_lines.append(line)
    if 'with schema_context(' in line and 'public' in line and line.strip().endswith(':'):
        # Check next line (if exists) and fix its indentation
        if i+1 < len(lines):
            next_line = lines[i+1]
            # If next line starts with less than 4 spaces or not indented, add indentation
            # We want 4 spaces minimum. Since we are inside a with block after the function's with schema_context(tenant.schema_name), 
            # we need to ensure the next line has 4 spaces more than current block's indent.
            # Let's compute the current indent level of the line with "with schema_context('public'):"
            current_indent = len(line) - len(line.lstrip())
            # Desired indent for next line = current_indent + 4 (one level)
            desired = current_indent + 4
            # Replace next line's indentation
            next_line_stripped = next_line.lstrip()
            if next_line_stripped.startswith('fee_settings'):
                # This is the line we need to fix
                next_line_fixed = ' ' * desired + next_line_stripped
                # Replace the next line in the list (we will not add the original next line now, we'll add fixed)
                # Instead, we will skip adding the original next line and add the fixed one after the with line
                # We'll add it after the with line (so we will modify new_lines accordingly)
                # But we already added the 'with' line. Now we need to add the fixed line as separate.
                new_lines.append(next_line_fixed)
                i += 1  # skip the original next line
    i += 1

# Write back
with open(file_path, "w") as f:
    f.writelines(new_lines)

print("✅ Fixed indentation in fee_generate view")
