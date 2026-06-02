#!/usr/bin/env python3
"""
Fix syntax error in axis_saas/public_urls.py
- Corrects the gym_reports URL pattern.
- Ensures all API endpoints are properly placed.
"""

import os
import re

def fix_public_urls():
    urls_path = os.path.join('axis_saas', 'public_urls.py')
    if not os.path.exists(urls_path):
        print(f"❌ {urls_path} not found.")
        return False

    with open(urls_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find the broken part and replace the entire urlpatterns block
    # We'll reconstruct the correct urlpatterns list from the existing content
    # The error is between "path('portal/<slug:schema_name>/gym/reports/'," and "eports_view, name='gym_reports'),"
    # We'll replace the whole gym_reports line and ensure API endpoints are after it.

    # First, locate the start of urlpatterns
    start_idx = content.find('urlpatterns = [')
    if start_idx == -1:
        print("Could not find urlpatterns definition.")
        return False

    # Extract the part before and after the urlpatterns block
    before = content[:start_idx]
    # We'll reconstruct the entire urlpatterns block
    patterns_block = content[start_idx:]

    # Define the correct urlpatterns content
    corrected_urlpatterns = '''urlpatterns = [
    # ===== GYM ROUTES (FIXED ORDER) =====
    path('portal/<slug:schema_name>/gym/customers/<int:customer_id>/generate-subscription/', portal_wrapper(login_required_for_schema(gym_generate_subscription)), name='gym_generate_subscription'),
    path('portal/<slug:schema_name>/gym/subscriptions/<int:subscription_id>/cancel/', portal_wrapper(login_required_for_schema(gym_cancel_subscription)), name='gym_cancel_subscription'),
    path('portal/<slug:schema_name>/gym/attendance/<int:attendance_id>/edit/', portal_wrapper(login_required_for_schema(gym_edit_attendance)), name='gym_edit_attendance'),
    # Gym subscription & cancellation routes
    path('api/debug-payments/', debug_payments_api, name='debug_payments_api'),
    path('', saas_homepage),
    path('admin/', admin.site.urls),
    path('api/fee-status/', fee_status_api, name='fee_status_api'),
    path('api/manual-generate/', manual_generate_api, name='manual_generate_api'),
    path('api/manual-generate-single/', manual_generate_single_api, name='manual_generate_single_api'),
    
    # Auth
    path('portal/<slug:schema_name>/login/', school_login, name='school_login'),
    path('portal/<slug:schema_name>/login/', school_login, name='tenant_login'),
    path('portal/<slug:schema_name>/logout/', school_logout, name='school_logout'),
    path('portal/<slug:schema_name>/logout/', school_logout, name='tenant_logout'),
    
    # Core - using the wrapped views
    path('portal/<slug:schema_name>/', dashboard_view, name='dashboard'),
    path('portal/<slug:schema_name>/students/', student_list_view, name='student_list'),
    path('portal/<slug:schema_name>/students/add/', add_student_view, name='add_student'),
    path('portal/<slug:schema_name>/students/edit/<int:student_id>/', edit_student_view, name='edit_student'),
    path('portal/<slug:schema_name>/students/<int:student_id>/', student_profile_view, name='student_profile'),
    
    # Fee collection
    re_path(r'^portal/(?P<schema_name>[a-zA-Z0-9_-]+)/fee/collection/(?:(?P<student_id>\d+)/)?$', fee_collection_view, name='fee_collection'),
    path('portal/<slug:schema_name>/fee/receipt/<int:receipt_id>/', fee_receipt_view, name='fee_receipt'),
    path('portal/<slug:schema_name>/defaulters/', defaulters_view, name='defaulters'),
    path('portal/<slug:schema_name>/reports/', reports_view, name='reports'),
    path('portal/<slug:schema_name>/settings/', settings_view, name='settings'),
    path('portal/<slug:schema_name>/fee/structure/', fee_structure_view, name='fee_structure'),
    path('portal/<slug:schema_name>/fee/settings/', fee_settings_view, name='fee_settings'),
    path('portal/<slug:schema_name>/fee/family-payment/', family_payment_view, name='family_payment'),
    path('portal/<slug:schema_name>/api/student-search/', student_search_api_view, name='student_search_api'),
    path('portal/<slug:schema_name>/api/student/<int:student_id>/fee-records/', student_fee_records_api_view, name='student_fee_records_api'),
    path('portal/<slug:schema_name>/api/student/<int:student_id>/payments/', student_payments_api_view, name='student_payments_api'),
    
    # Gym API
    path('api/gym/checkin/', gym_checkin_api, name='gym_checkin_api'),
    path('api/gym/checkout/', gym_checkout_api, name='gym_checkout_api'),
    path('portal/<slug:schema_name>/gym/receipt/<int:receipt_id>/', gym_receipt, name='gym_receipt'),

    # Gym routes
    path('portal/<slug:schema_name>/gym/', gym_dashboard_view, name='gym_dashboard'),
    path('portal/<slug:schema_name>/gym/customers/', gym_customer_list_view, name='gym_customer_list'),
    path('portal/<slug:schema_name>/gym/customers/add/', gym_customer_add_view, name='gym_customer_add'),
    path('portal/<slug:schema_name>/gym/customers/edit/<int:customer_id>/', gym_customer_edit_view, name='gym_customer_edit'),
    path('portal/<slug:schema_name>/gym/customers/<int:customer_id>/', gym_customer_profile_view, name='gym_customer_profile'),
    path('portal/<slug:schema_name>/gym/attendance/', gym_attendance_view, name='gym_attendance'),
    path('portal/<slug:schema_name>/gym/payments/', gym_payment_view, name='gym_payment'),
    path('portal/<slug:schema_name>/gym/payments/<int:customer_id>/', gym_payment_view, name='gym_payment'),
    path('portal/<slug:schema_name>/gym/reports/', gym_reports_view, name='gym_reports'),
    
    # Gym Reports API endpoints
    path('api/gym/revenue-stats/<slug:schema_name>/', gym_revenue_stats_api, name='gym_revenue_stats_api'),
    path('api/gym/attendance-stats/<slug:schema_name>/', gym_attendance_stats_api, name='gym_attendance_stats_api'),
    path('api/gym/customers-list/<slug:schema_name>/', gym_customers_list_api, name='gym_customers_list_api'),
    path('api/gym/customer-detail/<slug:schema_name>/<int:customer_id>/', gym_customer_detail_api, name='gym_customer_detail_api'),
    path('api/gym/subscription-status/<slug:schema_name>/', gym_subscription_status_api, name='gym_subscription_status_api'),
    
    path('portal/<slug:schema_name>/gym/settings/', gym_settings_view, name='gym_settings'),
]'''

    # Replace the entire urlpatterns block
    new_content = before + corrected_urlpatterns
    with open(urls_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print("✅ Fixed public_urls.py")
    return True

if __name__ == '__main__':
    fix_public_urls()
