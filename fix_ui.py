#!/usr/bin/env python3
"""
AXIS School System UI Fixer
- When sidebar is collapsed, profile dropdown opens OUTSIDE the sidebar (to the right)
- Dropdown always stays fully visible (auto‑repositions)
- Sidebar remains fixed while main content scrolls
"""

import re
import os

BASE_HTML = "templates/tenant/base.html"

def apply_fixes():
    if not os.path.exists(BASE_HTML):
        print(f"❌ Error: {BASE_HTML} not found. Run from project root.")
        return False

    with open(BASE_HTML, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Ensure sidebar is truly fixed
    fixed_css = """
        /* Make sidebar fixed, main content scrolls normally */
        html, body {
            height: 100%;
            margin: 0;
            padding: 0;
        }
        body {
            overflow-y: auto;
        }
        .sidebar {
            position: fixed;
            top: 0;
            left: 0;
            bottom: 0;
            width: 280px;
            overflow-y: hidden;
            z-index: 100;
        }
        .sidebar-nav {
            overflow-y: auto;
            flex: 1;
        }
        .main-content {
            margin-left: 280px;
            min-height: 100vh;
        }
        .sidebar.collapsed ~ .main-content {
            margin-left: 80px;
        }
        @media (max-width: 768px) {
            .main-content {
                margin-left: 0;
            }
        }
    """
    # Insert the fixed CSS before the last </style>
    if '</style>' in content:
        content = content.replace('</style>', fixed_css + '\n</style>', 1)
    else:
        content = content.replace('</head>', f'<style>{fixed_css}</style>\n</head>', 1)

    # 2. Replace the profile dropdown CSS so it always appears properly
    #    Remove any position:static and other conflicting rules for collapsed state
    #    We'll let JavaScript handle positioning.
    dropdown_css_cleanup = """
        /* Override any conflicting rules for collapsed sidebar dropdown */
        .sidebar.collapsed .profile-dropdown {
            position: relative;
        }
        .sidebar.collapsed .dropdown-menu {
            position: fixed !important;
            top: auto !important;
            bottom: auto !important;
            left: auto !important;
            right: auto !important;
            z-index: 10000;
            min-width: 200px;
        }
        /* Ensure dropdown never gets hidden */
        .dropdown-menu {
            z-index: 10000 !important;
        }
    """
    content = content.replace('</style>', dropdown_css_cleanup + '\n</style>', 1)

    # 3. Replace the entire dropdown JavaScript with a robust version
    new_js = """
    <script>
        // Profile dropdown - works in expanded & collapsed sidebar
        (function() {
            const profileBtn = document.getElementById('profileBtn');
            const dropdown = document.getElementById('profileDropdown');
            const sidebar = document.getElementById('sidebar');

            if (!profileBtn || !dropdown) return;

            function positionDropdown() {
                if (!dropdown.classList.contains('show')) return;

                const rect = profileBtn.getBoundingClientRect();
                const dropdownHeight = dropdown.offsetHeight;
                const dropdownWidth = dropdown.offsetWidth;
                const viewportWidth = window.innerWidth;
                const viewportHeight = window.innerHeight;

                // Always use fixed positioning
                dropdown.style.position = 'fixed';
                dropdown.style.margin = '0';
                dropdown.style.left = 'auto';
                dropdown.style.right = 'auto';

                // Determine if sidebar is collapsed
                const isCollapsed = sidebar && sidebar.classList.contains('collapsed');

                // Horizontal position: if collapsed, place dropdown to the right of the button
                if (isCollapsed) {
                    // Button is near left edge (80px sidebar)
                    // Place dropdown just to the right of the button
                    let leftPos = rect.right + 5;  // 5px gap
                    if (leftPos + dropdownWidth > viewportWidth) {
                        // Not enough space on right, align to left edge of button
                        leftPos = rect.left;
                    }
                    dropdown.style.left = leftPos + 'px';
                    dropdown.style.right = 'auto';
                } else {
                    // Normal expanded sidebar: align with button's left edge
                    if (rect.left + dropdownWidth > viewportWidth) {
                        dropdown.style.right = (viewportWidth - rect.right) + 'px';
                        dropdown.style.left = 'auto';
                    } else {
                        dropdown.style.left = rect.left + 'px';
                        dropdown.style.right = 'auto';
                    }
                }

                // Vertical position: open upward if not enough space below
                const spaceBelow = viewportHeight - rect.bottom;
                const spaceAbove = rect.top;
                if (spaceBelow < dropdownHeight && spaceAbove > dropdownHeight) {
                    // Open upward
                    dropdown.style.bottom = (viewportHeight - rect.top) + 'px';
                    dropdown.style.top = 'auto';
                } else {
                    // Open downward (default)
                    dropdown.style.top = rect.bottom + 'px';
                    dropdown.style.bottom = 'auto';
                }
            }

            profileBtn.addEventListener('click', function(e) {
                e.stopPropagation();
                const isVisible = dropdown.classList.contains('show');
                if (isVisible) {
                    dropdown.classList.remove('show');
                } else {
                    dropdown.classList.add('show');
                    positionDropdown();
                }
            });

            // Reposition on window resize, scroll, or sidebar collapse/expand
            window.addEventListener('resize', function() {
                if (dropdown.classList.contains('show')) positionDropdown();
            });
            window.addEventListener('scroll', function() {
                if (dropdown.classList.contains('show')) positionDropdown();
            });

            // Observe sidebar class changes (collapse/expand)
            if (sidebar) {
                const observer = new MutationObserver(function(mutations) {
                    mutations.forEach(function(mutation) {
                        if (mutation.attributeName === 'class') {
                            if (dropdown.classList.contains('show')) positionDropdown();
                        }
                    });
                });
                observer.observe(sidebar, { attributes: true });
            }

            // Close dropdown when clicking outside
            document.addEventListener('click', function(e) {
                if (!profileBtn.contains(e.target) && !dropdown.contains(e.target)) {
                    dropdown.classList.remove('show');
                }
            });
            dropdown.addEventListener('click', function(e) {
                e.stopPropagation();
            });
        })();
    </script>
    """

    # Remove any existing profile dropdown script blocks
    content = re.sub(r'<script>\s*// Profile dropdown[\s\S]*?</script>', '', content, flags=re.DOTALL)
    content = re.sub(r'<script>\s*// Enhanced Profile Dropdown[\s\S]*?</script>', '', content, flags=re.DOTALL)
    content = re.sub(r'<script>\s*// Profile dropdown functionality with dynamic positioning[\s\S]*?</script>', '', content, flags=re.DOTALL)

    # Insert our new script just before </body>
    content = content.replace('</body>', new_js + '\n</body>', 1)

    # Write back
    with open(BASE_HTML, "w", encoding="utf-8") as f:
        f.write(content)

    print("✅ UI fixes applied to", BASE_HTML)
    print("   - Sidebar is fixed (does not scroll with page)")
    print("   - When sidebar is **collapsed**, the profile dropdown opens **outside** (to the right)")
    print("   - Dropdown auto‑repositions to stay fully on screen")
    print("\n👉 Refresh your browser (hard refresh: Ctrl+F5) and test:")
    print("   - Collapse the sidebar (click the arrow)")
    print("   - Click the profile button – the menu now appears to the right of the button, not inside the 80px sidebar.")
    return True

if __name__ == "__main__":
    apply_fixes()
