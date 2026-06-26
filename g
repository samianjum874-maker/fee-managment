#!/usr/bin/env python3
"""
AXIS Mobile Student List – Premium UI/UX Upgrade v2
Replaces templates/mobile/student_list.html with a modern, premium design.
Run: python patch_mobile_student_list_ui_v2.py
"""

import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
TEMPLATE_PATH = PROJECT_ROOT / "templates" / "mobile" / "student_list.html"

NEW_TEMPLATE = """{% extends 'mobile/base.html' %}
{% load fee_extras %}
{% block title %}Students | {{ tenant.name }}{% endblock %}

{% block extra_head %}
<style>
  /* ---- Premium Mobile Student List ---- */
  :root {
    --card-shadow: 0 8px 24px rgba(15,23,42,0.06);
    --card-radius: 1.25rem;
    --glass-bg: rgba(255,255,255,0.88);
    --glass-border: rgba(255,255,255,0.5);
  }

  .page-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1rem;
    padding: 0 0.25rem;
  }
  .page-header h1 {
    font-size: 1.6rem;
    font-weight: 700;
    margin: 0;
    background: linear-gradient(135deg, var(--primary), var(--primary-dark));
    -webkit-background-clip: text;
    background-clip: text;
    color: transparent;
  }

  /* ---- Sticky Search Bar ---- */
  .search-sticky {
    position: sticky;
    top: 0;
    z-index: 10;
    background: var(--bg);
    padding: 0.5rem 0 0.75rem;
    backdrop-filter: blur(8px);
    -webkit-backdrop-filter: blur(8px);
  }
  .search-bar {
    display: flex;
    gap: 0.5rem;
    align-items: center;
    background: var(--glass-bg);
    backdrop-filter: blur(8px);
    -webkit-backdrop-filter: blur(8px);
    border-radius: 2.5rem;
    padding: 0.3rem 0.3rem 0.3rem 1rem;
    border: 1px solid var(--glass-border);
    box-shadow: var(--card-shadow);
  }
  .search-bar input {
    flex: 1;
    border: none;
    background: transparent;
    font-size: 0.95rem;
    padding: 0.5rem 0;
    outline: none;
    color: var(--text);
  }
  .search-bar input::placeholder {
    color: var(--muted);
  }
  .search-bar button {
    background: var(--primary);
    color: white;
    border: none;
    border-radius: 2rem;
    padding: 0.5rem 1.2rem;
    font-weight: 600;
    font-size: 0.85rem;
    cursor: pointer;
    transition: background 0.2s;
    white-space: nowrap;
  }
  .search-bar button:hover {
    background: var(--primary-dark);
  }
  .filter-toggle {
    background: transparent;
    border: none;
    color: var(--muted);
    padding: 0.3rem;
    cursor: pointer;
    display: flex;
    align-items: center;
    gap: 0.2rem;
    font-size: 0.8rem;
  }
  .filter-toggle svg {
    width: 20px;
    height: 20px;
  }

  /* ---- Filter Drawer (slide down) ---- */
  .filter-drawer {
    max-height: 0;
    overflow: hidden;
    transition: max-height 0.3s ease, padding 0.3s ease;
    padding: 0 0.5rem;
    background: var(--glass-bg);
    backdrop-filter: blur(8px);
    -webkit-backdrop-filter: blur(8px);
    border-radius: 0 0 1.25rem 1.25rem;
    margin: 0 0 1rem 0;
    border-left: 1px solid var(--glass-border);
    border-right: 1px solid var(--glass-border);
    border-bottom: 1px solid var(--glass-border);
    box-shadow: var(--card-shadow);
  }
  .filter-drawer.open {
    max-height: 300px;
    padding: 0.75rem 0.5rem;
  }
  .filter-drawer .filter-grid {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
  }
  .filter-drawer select {
    flex: 1 1 120px;
    padding: 0.4rem 0.6rem;
    border-radius: 2rem;
    border: 1px solid var(--border);
    background: var(--surface-alt);
    font-size: 0.85rem;
  }
  .filter-drawer .clear-link {
    background: var(--surface-alt);
    color: var(--text);
    padding: 0.4rem 1rem;
    border-radius: 2rem;
    border: 1px solid var(--border);
    font-weight: 500;
    text-decoration: none;
    font-size: 0.85rem;
    display: inline-flex;
    align-items: center;
    gap: 0.3rem;
  }

  /* ---- Student Cards ---- */
  .student-card {
    background: var(--glass-bg);
    backdrop-filter: blur(8px);
    -webkit-backdrop-filter: blur(8px);
    border-radius: var(--card-radius);
    padding: 0.9rem 1rem;
    margin-bottom: 0.85rem;
    border: 1px solid var(--glass-border);
    box-shadow: var(--card-shadow);
    display: flex;
    align-items: center;
    gap: 0.8rem;
    transition: transform 0.15s ease, box-shadow 0.2s;
  }
  .student-card:active {
    transform: scale(0.99);
  }
  .student-avatar {
    width: 48px;
    height: 48px;
    border-radius: 50%;
    background: linear-gradient(135deg, var(--primary), var(--primary-dark));
    color: white;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 700;
    font-size: 1.2rem;
    flex-shrink: 0;
  }
  .student-info {
    flex: 1;
    min-width: 0;
  }
  .student-name {
    font-weight: 700;
    font-size: 1.05rem;
    color: var(--text);
  }
  .student-meta {
    font-size: 0.82rem;
    color: var(--muted);
    margin-top: 0.1rem;
  }
  .student-meta .badge {
    display: inline-block;
    padding: 0.1rem 0.5rem;
    border-radius: 999px;
    font-size: 0.65rem;
    font-weight: 600;
    margin-left: 0.3rem;
  }
  .badge-active { background: #d1fae5; color: #065f46; }
  .badge-suspended { background: #fed7aa; color: #9a3412; }
  .badge-graduated { background: #e0e7ff; color: #3730a3; }
  .student-pending {
    font-weight: 600;
    color: var(--danger);
    font-size: 0.9rem;
    margin-top: 0.1rem;
  }
  .student-actions {
    display: flex;
    gap: 0.3rem;
    flex-shrink: 0;
  }
  .student-actions a {
    background: var(--surface-alt);
    border: 1px solid var(--border);
    border-radius: 2rem;
    padding: 0.25rem 0.6rem;
    font-size: 0.7rem;
    font-weight: 600;
    text-decoration: none;
    color: var(--text);
    transition: all 0.2s;
    display: flex;
    align-items: center;
    gap: 0.2rem;
  }
  .student-actions a:hover {
    background: var(--primary);
    color: white;
    border-color: var(--primary);
  }
  .student-actions a svg {
    width: 14px;
    height: 14px;
  }

  /* ---- Pagination ---- */
  .pagination {
    display: flex;
    justify-content: center;
    gap: 0.4rem;
    margin-top: 1.2rem;
    flex-wrap: wrap;
  }
  .pagination a, .pagination span {
    padding: 0.3rem 0.8rem;
    border-radius: 2rem;
    border: 1px solid var(--border);
    background: var(--surface);
    text-decoration: none;
    color: var(--text);
    font-size: 0.8rem;
    transition: all 0.2s;
  }
  .pagination a:hover {
    background: var(--primary);
    color: white;
    border-color: var(--primary);
  }
  .pagination .active {
    background: var(--primary);
    color: white;
    border-color: var(--primary);
  }
  .pagination .disabled {
    opacity: 0.4;
    pointer-events: none;
  }

  /* ---- Empty State ---- */
  .empty-state {
    text-align: center;
    padding: 3rem 1rem;
    color: var(--muted);
  }
  .empty-state svg {
    opacity: 0.3;
    margin-bottom: 0.5rem;
  }
  .empty-state a {
    color: var(--primary);
    font-weight: 600;
    text-decoration: none;
  }

  /* ---- FAB (Floating Action Button) ---- */
  .fab-add {
    position: fixed;
    bottom: 90px;
    right: 1.2rem;
    background: var(--primary);
    color: white;
    border: none;
    border-radius: 999px;
    width: 56px;
    height: 56px;
    font-size: 1.8rem;
    box-shadow: 0 8px 24px rgba(59,130,246,0.35);
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 20;
    transition: transform 0.2s, box-shadow 0.2s;
  }
  .fab-add:active {
    transform: scale(0.92);
  }

  /* ---- Responsive ---- */
  @media (max-width: 480px) {
    .student-card {
      flex-wrap: wrap;
    }
    .student-actions {
      width: 100%;
      justify-content: flex-end;
    }
    .search-bar input {
      font-size: 0.85rem;
    }
    .filter-toggle span {
      display: none;
    }
  }
</style>
{% endblock %}

{% block body %}
<div class="page-header">
  <h1>Students</h1>
  <div style="font-size:0.8rem; color:var(--muted);">
    {{ students.paginator.count|default:0 }} total
  </div>
</div>

<!-- Sticky Search & Filter -->
<div class="search-sticky">
  <div class="search-bar">
    <input type="search" id="searchInput" placeholder="Search name, roll, father..." value="{{ search_query }}" autocomplete="off">
    <button id="searchBtn">Search</button>
    <button class="filter-toggle" id="filterToggle" aria-label="Toggle filters">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M4 6h16M4 12h16M4 18h16"/>
      </svg>
      <span>Filters</span>
    </button>
  </div>
  <div class="filter-drawer" id="filterDrawer">
    <div class="filter-grid">
      <select name="grade" id="gradeSelect">
        <option value="">All Grades</option>
        {% for g in grades %}
        <option value="{{ g }}" {% if request.GET.grade == g %}selected{% endif %}>{{ g }}</option>
        {% endfor %}
      </select>
      <select name="section" id="sectionSelect">
        <option value="">All Sections</option>
        {% for s in sections %}
        <option value="{{ s }}" {% if request.GET.section == s %}selected{% endif %}>{{ s }}</option>
        {% endfor %}
      </select>
      <select name="status" id="statusSelect">
        <option value="">All Status</option>
        {% for k,v in status_choices %}
        <option value="{{ k }}" {% if request.GET.status == k %}selected{% endif %}>{{ v }}</option>
        {% endfor %}
      </select>
      <a href="{% url 'mobile_student_list' schema_name=tenant.schema_name %}" class="clear-link">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M6 18L18 6M6 6l12 12"/></svg>
        Clear
      </a>
    </div>
  </div>
</div>

<!-- Student Cards -->
<div id="studentContainer">
  {% if students %}
    {% for s in students %}
    <div class="student-card" data-name="{{ s.name|lower }}" data-roll="{{ s.roll_number|lower }}" data-father="{{ s.father_name|lower }}">
      <div class="student-avatar">{{ s.name|slice:":1"|upper }}</div>
      <div class="student-info">
        <div class="student-name">{{ s.name }}</div>
        <div class="student-meta">
          {{ s.grade }} • {{ s.section }} • Roll {{ s.roll_number }}
          <span class="badge badge-{{ s.status }}">{{ s.get_status_display }}</span>
        </div>
        <div class="student-meta">Father: {{ s.father_name }}</div>
        <div class="student-pending">Pending: ₹{{ s.pending_amount|floatformat:2 }}</div>
      </div>
      <div class="student-actions">
        <a href="{% url 'mobile_student_profile' schema_name=tenant.schema_name student_id=s.id %}" title="Profile">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/><path d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/></svg>
        </a>
        <a href="{% url 'mobile_fee_collection' schema_name=tenant.schema_name student_id=s.id %}" title="Collect">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17 9V7a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2m2 4h10a2 2 0 002-2v-6a2 2 0 00-2-2H9a2 2 0 00-2 2v6a2 2 0 002 2z"/></svg>
        </a>
      </div>
    </div>
    {% endfor %}

    <!-- Pagination -->
    <div class="pagination">
      {% if students.has_previous %}
        <a href="?page=1{% if search_query %}&q={{ search_query }}{% endif %}{% if request.GET.grade %}&grade={{ request.GET.grade }}{% endif %}{% if request.GET.section %}&section={{ request.GET.section }}{% endif %}{% if request.GET.status %}&status={{ request.GET.status }}{% endif %}">First</a>
        <a href="?page={{ students.previous_page_number }}{% if search_query %}&q={{ search_query }}{% endif %}{% if request.GET.grade %}&grade={{ request.GET.grade }}{% endif %}{% if request.GET.section %}&section={{ request.GET.section }}{% endif %}{% if request.GET.status %}&status={{ request.GET.status }}{% endif %}">‹</a>
      {% else %}
        <span class="disabled">First</span>
        <span class="disabled">‹</span>
      {% endif %}

      <span class="active">Page {{ students.number }} of {{ students.paginator.num_pages }}</span>

      {% if students.has_next %}
        <a href="?page={{ students.next_page_number }}{% if search_query %}&q={{ search_query }}{% endif %}{% if request.GET.grade %}&grade={{ request.GET.grade }}{% endif %}{% if request.GET.section %}&section={{ request.GET.section }}{% endif %}{% if request.GET.status %}&status={{ request.GET.status }}{% endif %}">›</a>
        <a href="?page={{ students.paginator.num_pages }}{% if search_query %}&q={{ search_query }}{% endif %}{% if request.GET.grade %}&grade={{ request.GET.grade }}{% endif %}{% if request.GET.section %}&section={{ request.GET.section }}{% endif %}{% if request.GET.status %}&status={{ request.GET.status }}{% endif %}">Last</a>
      {% else %}
        <span class="disabled">›</span>
        <span class="disabled">Last</span>
      {% endif %}
    </div>
  {% else %}
    <div class="empty-state">
      <svg width="56" height="56" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
        <circle cx="12" cy="12" r="10"/>
        <path d="M8 12h8"/>
      </svg>
      <p>No students found.</p>
      <a href="{% url 'add_student_mobile' schema_name=tenant.schema_name %}">Add your first student</a>
    </div>
  {% endif %}
</div>

<!-- FAB for Add -->
<a href="{% url 'add_student_mobile' schema_name=tenant.schema_name %}" class="fab-add" aria-label="Add Student">
  <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M12 4v16m8-8H4"/></svg>
</a>

<script>
  (function() {
    // Toggle filter drawer
    const toggleBtn = document.getElementById('filterToggle');
    const drawer = document.getElementById('filterDrawer');
    toggleBtn.addEventListener('click', function(e) {
      e.preventDefault();
      drawer.classList.toggle('open');
    });

    // Search: live filtering with debounce
    const searchInput = document.getElementById('searchInput');
    const searchBtn = document.getElementById('searchBtn');
    const gradeSelect = document.getElementById('gradeSelect');
    const sectionSelect = document.getElementById('sectionSelect');
    const statusSelect = document.getElementById('statusSelect');

    function buildUrl() {
      const params = new URLSearchParams();
      const q = searchInput.value.trim();
      if (q) params.set('q', q);
      if (gradeSelect.value) params.set('grade', gradeSelect.value);
      if (sectionSelect.value) params.set('section', sectionSelect.value);
      if (statusSelect.value) params.set('status', statusSelect.value);
      const url = window.location.pathname + '?' + params.toString();
      return url;
    }

    function applyFilters() {
      window.location.href = buildUrl();
    }

    // On button click
    searchBtn.addEventListener('click', applyFilters);

    // Enter key in search input
    searchInput.addEventListener('keypress', function(e) {
      if (e.key === 'Enter') {
        e.preventDefault();
        applyFilters();
      }
    });

    // Auto‑submit on select change (optional, but nice)
    gradeSelect.addEventListener('change', applyFilters);
    sectionSelect.addEventListener('change', applyFilters);
    statusSelect.addEventListener('change', applyFilters);

    // If there is a search query, keep the input value (it's already there from template)
    // Ensure filter drawer is open if any filter is active
    const hasFilters = {{ request.GET.grade|yesno:"true,false" }} || {{ request.GET.section|yesno:"true,false" }} || {{ request.GET.status|yesno:"true,false" }};
    if (hasFilters) {
      drawer.classList.add('open');
    }

    // Live client‑side filtering (optional, but for instant feedback we can add a simple filter)
    // For now, we rely on server‑side pagination, which is better for large datasets.
  })();
</script>
{% endblock %}
"""

def main():
    # Ensure directory exists
    TEMPLATE_PATH.parent.mkdir(parents=True, exist_ok=True)

    with open(TEMPLATE_PATH, "w") as f:
        f.write(NEW_TEMPLATE)

    print(f"✅ Updated {TEMPLATE_PATH} with premium UI v2.")
    print("✅ Features: sticky search, filter drawer, FAB, avatar cards.")
    print("🔄 Clear your browser cache and hard reload (Ctrl+F5 or Cmd+Shift+R).")
    print("▶️ Restart server: python manage.py runserver")

if __name__ == "__main__":
    main()
