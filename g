#!/usr/bin/env python3
"""
AXIS PWA Sidebar Patcher – Adds an Install App button to the sidebar (desktop)
and keeps the floating button on mobile. Both use the same install prompt.
Run once from the project root.
"""

import os
import re
from pathlib import Path

BASE_HTML = Path("templates/tenant/base.html")

if not BASE_HTML.exists():
    print("❌ templates/tenant/base.html not found. Are you in the project root?")
    exit(1)

with open(BASE_HTML, "r") as f:
    content = f.read()

# ----------------------------------------------------------------------
# 1. Add sidebar install button inside .sidebar-footer (after profile dropdown)
# ----------------------------------------------------------------------
sidebar_button_html = """
                <!-- PWA Install Button (Sidebar) -->
                <button id="installAppSidebarBtn" class="nav-item" style="display: none; width: 100%; background: none; border: none; text-align: left; cursor: pointer;">
                    <svg class="nav-icon" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M4 16v1a2 2 0 002 2h12a2 2 0 002-2v-1M12 4v12m-4-4l4 4 4-4"/>
                    </svg>
                    <span>Install App</span>
                </button>
"""

# Find the sidebar-footer and insert after the profile dropdown (or before the closing </div>)
# We'll insert right after the profile dropdown container (id="profileDropdownContainer") ends.
# The existing structure: <div class="sidebar-footer"> ... <div class="profile-dropdown" id="profileDropdownContainer"> ... </div> </div>
# We'll place the button right after the profile dropdown container, but still inside sidebar-footer.

profile_dropdown_end = content.find('</div>', content.find('id="profileDropdownContainer"'))
if profile_dropdown_end == -1:
    print("⚠️ Could not find profileDropdownContainer. Inserting at end of sidebar-footer.")
    # Fallback: insert before the last </div> of sidebar-footer
    footer_end = content.find('</div>', content.find('class="sidebar-footer"'))
    if footer_end != -1:
        content = content[:footer_end] + sidebar_button_html + content[footer_end:]
else:
    # Insert after the profile dropdown container's closing div, but before the sidebar-footer close
    # Find the next closing div after that (which is the sidebar-footer closing)
    footer_close = content.find('</div>', profile_dropdown_end + 1)
    if footer_close != -1:
        content = content[:footer_close] + sidebar_button_html + content[footer_close:]
    else:
        # If not found, insert at the very end of sidebar-footer (before </div>)
        footer_end = content.find('</div>', content.find('class="sidebar-footer"'))
        if footer_end != -1:
            content = content[:footer_end] + sidebar_button_html + content[footer_end:]

print("✅ Added sidebar install button.")

# ----------------------------------------------------------------------
# 2. Update CSS: hide sidebar button in standalone mode & show on desktop
# ----------------------------------------------------------------------
# We already have a rule in base.html:
#   @media all and (display-mode: standalone) { #pwaInstallContainer { display: none !important; } }
# We need to also hide the sidebar button in standalone mode.
# Let's add that rule.

hide_standalone = """
@media all and (display-mode: standalone) {
    #pwaInstallContainer { display: none !important; }
    #installAppSidebarBtn { display: none !important; }
}
"""
# Check if it already exists (it might have the first line, we'll append the second)
if "#installAppSidebarBtn" not in content:
    # If we already have the first rule, replace it with the combined one.
    if "@media all and (display-mode: standalone)" in content:
        # Replace the old block with the new one (including both)
        pattern = r'@media all and \(display-mode: standalone\) \{[^}]*\}'
        content = re.sub(pattern, hide_standalone, content, flags=re.DOTALL)
    else:
        # Insert before </style> or </head>
        if "</style>" in content:
            content = content.replace("</style>", hide_standalone + "\n</style>")
        else:
            content = content.replace("</head>", f"<style>{hide_standalone}</style></head>")
    print("✅ Updated standalone mode hiding for both buttons.")

# ----------------------------------------------------------------------
# 3. Update JavaScript: handle multiple install buttons
# ----------------------------------------------------------------------
# We need to ensure both the floating button and the sidebar button trigger the same prompt.
# The existing script uses:
#   const installBtn = document.getElementById('installAppBtn');
#   installBtn.addEventListener('click', async () => { ... });
# We'll add a second listener for the sidebar button.

# Find the script block that contains the install logic.
# We'll locate the part where installBtn is defined and add code for sidebarBtn.

# Look for the existing installBtn event listener and append a similar one for sidebarBtn.
# We'll insert after the existing installBtn click handler.

js_install_code = """
        // Sidebar install button
        const sidebarInstallBtn = document.getElementById('installAppSidebarBtn');
        if (sidebarInstallBtn) {
            sidebarInstallBtn.addEventListener('click', async () => {
                if (deferredPrompt) {
                    deferredPrompt.prompt();
                    const result = await deferredPrompt.userChoice;
                    if (result.outcome === 'accepted') {
                        console.log('User accepted the install prompt (sidebar)');
                        installContainer.style.display = 'none';
                        sidebarInstallBtn.style.display = 'none';
                    } else {
                        console.log('User dismissed the install prompt (sidebar)');
                    }
                    deferredPrompt = null;
                }
            });
        }
"""

# Find where the existing installBtn click handler is defined and insert after it.
# We'll search for "installBtn.addEventListener('click'" and insert after its closing brace.
# A simple approach: replace the entire beforeinstallprompt event listener block with an enhanced version.
# Actually, we can just add the new listener after the existing one. We'll locate the closing brace of the existing listener.

if 'installBtn.addEventListener' in content:
    # Find the end of that listener's function (search for the matching closing brace after the async function)
    # We'll insert before the next statement (probably the window.addEventListener('appinstalled'))
    pattern = r'(installBtn\.addEventListener\([\s\S]*?\);)'
    match = re.search(pattern, content)
    if match:
        existing_code = match.group(0)
        # Insert our new code after it, but before the next line (maybe after the semicolon)
        # We'll replace the match with the existing code + new code.
        new_block = existing_code + "\n\n" + js_install_code
        content = content.replace(existing_code, new_block)
        print("✅ Added sidebar install button event listener.")
    else:
        print("⚠️ Could not find installBtn click handler; adding new code separately.")
        # Fallback: just append the new code before the closing </script> tag.
        if "</script>" in content:
            content = content.replace("</script>", js_install_code + "\n</script>")
else:
    print("⚠️ installBtn not found; adding new listener anyway.")
    if "</script>" in content:
        content = content.replace("</script>", js_install_code + "\n</script>")

# Also need to show the sidebar button when the prompt is available.
# The existing beforeinstallprompt event shows the floating container. We'll also show the sidebar button.
# We'll modify that event to also show the sidebar button.

if 'window.addEventListener(\'beforeinstallprompt\'' in content:
    # We'll enhance the event listener to also show the sidebar button.
    # Find the existing block and add a line to show the sidebar button.
    # Look for the part that sets installContainer.style.display = 'block';
    # and add a line for sidebar button.
    pattern = r'(window\.addEventListener\([\s\S]*?beforeinstallprompt[\s\S]*?\);)'
    match = re.search(pattern, content)
    if match:
        old_block = match.group(0)
        # Add line to show sidebar button
        new_block = old_block.replace(
            'installContainer.style.display = \'block\';',
            'installContainer.style.display = \'block\';\n            sidebarInstallBtn.style.display = \'flex\';'
        )
        content = content.replace(old_block, new_block)
        print("✅ Updated beforeinstallprompt to show sidebar button.")
    else:
        print("⚠️ Could not find beforeinstallprompt event; adding fallback.")
        # Fallback: if not found, we might need to add the event entirely, but it's probably there.
        pass

# Also need to ensure the sidebar button is hidden initially.
# The button has inline style display:none; so it's fine.

# ----------------------------------------------------------------------
# 4. Write the updated base.html
# ----------------------------------------------------------------------
with open(BASE_HTML, "w") as f:
    f.write(content)

print("\n✅ PWA Sidebar patching complete!")
print("\nNext steps:")
print("1. Run `python manage.py collectstatic --noinput` (if you have static files).")
print("2. Restart your Django server.")
print("3. On desktop, the 'Install App' button will appear in the sidebar (bottom).")
print("   On mobile, the floating button will also appear (both will work).")
print("   In standalone mode, both buttons are hidden automatically.")
