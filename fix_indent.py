import re

file_path = "axis_saas/public_urls.py"

with open(file_path, "r") as f:
    lines = f.readlines()

fixed_lines = []
i = 0
while i < len(lines):
    line = lines[i]
    # Look for "with schema_context('public'):"
    if line.strip().startswith("with schema_context('public'):"):
        fixed_lines.append(line)
        # Next line should be indented
        if i+1 < len(lines):
            next_line = lines[i+1]
            # If next line is not empty and not indented properly
            if next_line.strip() and not next_line.startswith('                '):
                # Add proper indentation (16 spaces based on current indent level)
                # Determine current indent of the 'with' line
                indent_match = re.match(r'^(\s*)', line)
                current_indent = indent_match.group(1) if indent_match else ''
                # Add 4 spaces more
                fixed_lines.append(current_indent + '    ' + next_line.lstrip())
                i += 1
            else:
                fixed_lines.append(next_line)
                i += 1
    else:
        fixed_lines.append(line)
    i += 1

with open(file_path, "w") as f:
    f.writelines(fixed_lines)

print("Indentation fixed")
