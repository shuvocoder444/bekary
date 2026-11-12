"""
Comprehensive Automated Test Suite for DHAT & Bakery Management System
Tests:
1. Health Check Endpoint
2. Dynamic Base Template Pattern (Single-Template Full vs HTMX Partial)
3. Authentication Flow (Standard & HTMX Redirects)
4. Site Settings CRUD & HTMX Out-Of-Band (OOB) Toasts & Logo Swap
5. Static & Environment Configuration
6. Production Batch Recipe Execution & Inventory Stock Movements
7. Hawker Delivery Challan & Due Balance Ledger Tracking
8. Global English <-> Bangla Language Switching
"""

import os
import sys
import django
from django.conf import settings

# Setup Django Environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from apps.site_settings.models import SiteSetting
from apps.inventory.models import RawMaterial, ProductionBatch, BatchConsumption, BatchOutput
from apps.products.models import Product, Category
from apps.orders.models import Customer, Order, OrderItem

User = get_user_model()


class HealthCheckTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_health_check_endpoint(self):
        """Validates that the /health/ endpoint returns HTTP 200 and healthy JSON."""
        response = self.client.get(reverse('health_check'))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data.get('status'), 'healthy')
        self.assertEqual(data.get('database'), 'connected')
        self.assertIn('timestamp', data)


class DynamicBaseTemplateTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email='testuser@example.com',
            password='SecretPassword123!',
            role='admin'
        )
        self.client.force_login(self.user)

    def test_unauthenticated_redirect(self):
        """Unauthenticated requests to protected dashboard routes must redirect to login."""
        self.client.logout()
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)

    def test_full_page_load_contains_layout_shell(self):
        """Direct browser request (non-HTMX) must render full base.html layout."""
        response = self.client.get(reverse('calendar'))
        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')

        # Must contain HTML shell elements
        self.assertIn('<!doctype html>', content.lower())
        self.assertIn('<main id="main-content">', content)
        self.assertIn('id="toast-container"', content)
        self.assertIn('id="loading-bar"', content)
        self.assertTrue('Calendar' in content or 'ক্যালেন্ডার' in content)

    def test_htmx_request_returns_only_partial_content(self):
        """HTMX boosted request must render only page content without duplicate base.html shell."""
        response = self.client.get(reverse('calendar'), HTTP_HX_REQUEST='true')
        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')

        # Must contain page specific content
        self.assertTrue('Calendar' in content or 'ক্যালেন্ডার' in content)

        # Must NOT contain duplicate outer shell tags
        self.assertNotIn('<!doctype html>', content.lower())
        self.assertNotIn('<html', content.lower())
        self.assertNotIn('<main id="main-content">', content)
        self.assertNotIn('id="loading-bar"', content)

    def test_all_core_dashboard_routes_render(self):
        """Verify that every dashboard route renders successfully with HTMX."""
        routes = ['dashboard', 'profile', 'task', 'forms', 'tables', 'pages', 'charts', 'ui_elements']
        for route_name in routes:
            response = self.client.get(reverse(route_name), HTTP_HX_REQUEST='true')
            self.assertEqual(response.status_code, 200, f"Route {route_name} failed to render")


class AuthenticationFlowTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.email = 'authuser@example.com'
        self.password = 'AuthPass123!'
        self.user = User.objects.create_user(
            email=self.email,
            password=self.password,
            role='manager'
        )

    def test_login_page_renders(self):
        """Login page loads with 200 OK for anonymous users."""
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)

    def test_login_with_invalid_credentials(self):
        """Invalid credentials show error without redirecting."""
        response = self.client.post(reverse('login'), {
            'username': self.email,
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')
        self.assertTrue(
            'Invalid credentials' in content or 'অ্যাকাউন্টের তথ্য সঠিক নয়' in content,
            "Error message not found in login response"
        )

    def test_standard_login_redirects(self):
        """Standard form submission redirects to dashboard with 302."""
        response = self.client.post(reverse('login'), {
            'username': self.email,
            'password': self.password
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('dashboard'))

    def test_htmx_login_returns_hx_redirect_header(self):
        """HTMX login request returns 200 with HX-Redirect header."""
        response = self.client.post(
            reverse('login'),
            {'username': self.email, 'password': self.password},
            HTTP_HX_REQUEST='true'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers.get('HX-Redirect'), reverse('dashboard'))

    def test_htmx_logout_returns_hx_redirect(self):
        """HTMX logout request returns HX-Redirect to login page."""
        self.client.force_login(self.user)
        response = self.client.get(reverse('logout'), HTTP_HX_REQUEST='true')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers.get('HX-Redirect'), reverse('login'))


class SiteSettingsAndToastOOBTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email='admin@example.com',
            password='AdminPassword123!',
            role='admin'
        )
        self.client.force_login(self.user)
        self.setting, _ = SiteSetting.objects.get_or_create(id=1, defaults={'site_name': 'Original Site'})

    def test_site_settings_get(self):
        """Site settings page renders properly."""
        response = self.client.get(reverse('site_settings'))
        self.assertEqual(response.status_code, 200)

    def test_site_settings_htmx_post_updates_and_swaps_toast_and_logo(self):
        """
        Validates the core AGENTS.md rules:
        1. Toast notifications rendered from templates/partials/toast.html
        2. Toast container positioned at fixed top-20 right-6 z-99999
        3. Returned with hx-swap-oob="true"
        4. Sidebar logo swapped with hx-swap-oob="outerHTML:#sidebar-logo"
        """
        payload = {
            'site_name': 'DHAT Enterprise System',
            'contact_email': 'contact@dhat.dev',
            'contact_phone': '+8801700000000',
            'address': 'Dhaka, Bangladesh',
            'currency_symbol': '৳',
        }
        response = self.client.post(
            reverse('site_settings'),
            data=payload,
            HTTP_HX_REQUEST='true'
        )
        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')

        # 1. Rule verification: Toast partial and position
        self.assertIn('id="toast-container"', content)
        self.assertIn('fixed top-20 right-6 z-99999', content)
        self.assertIn('hx-swap-oob="true"', content)
        self.assertTrue('Bakery settings updated successfully!' in content or 'সাইট সেটিংস সফলভাবে আপডেট করা হয়েছে!' in content)

        # 2. Rule verification: Targeted sidebar logo swap
        self.assertIn('hx-swap-oob="outerHTML:#sidebar-logo"', content)

        # 3. Database persistence
        self.setting.refresh_from_db()
        self.assertEqual(self.setting.site_name, 'DHAT Enterprise System')


class ProductionBatchExecutionTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(email='baker@example.com', password='pass', role='admin')
        self.client.force_login(self.user)

        self.oil = RawMaterial.objects.create(name='Soybean Oil', unit='kg', current_stock=20.0, unit_cost=150.0)
        self.flour = RawMaterial.objects.create(name='Bakery Flour', unit='kg', current_stock=50.0, unit_cost=45.0)
        self.eggs = RawMaterial.objects.create(name='Farm Eggs', unit='pcs', current_stock=100.0, unit_cost=11.5)

        cat, _ = Category.objects.get_or_create(name='Bread')
        self.bread = Product.objects.create(name='Pauroti (Bread)', category=cat, sku='SKU-BREAD-TEST', selling_price=35.0, stock_quantity=0)

    def test_production_batch_creation_deducts_materials_and_adds_products(self):
        """Production batch consumes exact raw materials and increases baked goods stock."""
        payload = {
            'production_date': '2026-11-11',
            'notes': 'Test morning baking batch',
            'material_id[]': [self.oil.id, self.flour.id, self.eggs.id],
            'material_qty[]': [2.0, 30.0, 4.0],
            'product_id[]': [self.bread.id],
            'product_qty[]': [50],
        }
        response = self.client.post(reverse('production_batch_create'), data=payload)
        self.assertEqual(response.status_code, 302)

        # Verify stock deductions
        self.oil.refresh_from_db()
        self.flour.refresh_from_db()
        self.eggs.refresh_from_db()
        self.assertEqual(self.oil.current_stock, 18.0)
        self.assertEqual(self.flour.current_stock, 20.0)
        self.assertEqual(self.eggs.current_stock, 96.0)

        # Verify product addition
        self.bread.refresh_from_db()
        self.assertEqual(self.bread.stock_quantity, 50)

        # Verify batch record and BOM costs
        batch = ProductionBatch.objects.first()
        self.assertIsNotNone(batch)
        expected_cost = (2.0 * 150.0) + (30.0 * 45.0) + (4.0 * 11.5)  # 300 + 1350 + 46 = 1696.0
        self.assertEqual(float(batch.total_raw_material_cost), expected_cost)


class HawkerDistributionAndLedgerTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(email='dispatch@example.com', password='pass', role='admin')
        self.client.force_login(self.user)

        cat, _ = Category.objects.get_or_create(name='Snacks')
        self.bon_bati = Product.objects.create(name='Bon+Bati', category=cat, sku='SKU-BONBATI-TEST', selling_price=16.0, stock_quantity=300)
        self.hawker = Customer.objects.create(name='Ali (Meherpur)', customer_type='hawker', running_due=9004.0, phone='01708559545')

    def test_hawker_dispatch_deducts_product_and_updates_running_due(self):
        """Hawker dispatch reduces finished goods stock and adjusts hawker running due balance."""
        payload = {
            'hawker_id': self.hawker.id,
            'dispatch_date': '2026-11-11',
            'product_id[]': [self.bon_bati.id],
            'quantity[]': [259],
            'rate[]': [16.0],
            'paid_amount': 3000.0,
            'payment_method': 'cash',
            'notes': 'Daily delivery route Meherpur',
        }
        response = self.client.post(reverse('hawker_dispatch_create'), data=payload)
        self.assertEqual(response.status_code, 302)

        # Check product stock
        self.bon_bati.refresh_from_db()
        self.assertEqual(self.bon_bati.stock_quantity, 300 - 259)

        # Check hawker due: previous 9004 + new delivery (259*16 = 4144) - cash paid 3000 = 9004 + 1144 = 10148.0
        self.hawker.refresh_from_db()
        self.assertEqual(float(self.hawker.running_due), 10148.0)


class LanguageSwitchingTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_switch_to_bangla_and_english(self):
        """Switch language endpoint sets session and returns 302."""
        res_bn = self.client.get(reverse('switch_language') + '?lang=bn&next=/dashboard/')
        self.assertEqual(res_bn.status_code, 302)
        self.assertEqual(self.client.session.get('django_language'), 'bn')

        res_en = self.client.get(reverse('switch_language') + '?lang=en&next=/dashboard/')
        self.assertEqual(res_en.status_code, 302)
        self.assertEqual(self.client.session.get('django_language'), 'en')


class ConfigurationIntegrityTests(TestCase):
    def test_tailwind_source_outside_static(self):
        """Confirms that Tailwind CLI source CSS is placed in assets/ to prevent collectstatic crashes."""
        self.assertTrue(os.path.exists(settings.TAILWIND_CLI_SRC_CSS))
        self.assertIn('assets', settings.TAILWIND_CLI_SRC_CSS)

    def test_context_processors_registered(self):
        """Verifies that base_template context processor is active."""
        options = settings.TEMPLATES[0]['OPTIONS']
        self.assertIn('config.context_processors.base_template', options['context_processors'])


if __name__ == '__main__':
    from django.test.runner import DiscoverRunner
    test_runner = DiscoverRunner(verbosity=2, interactive=False)
    failures = test_runner.run_tests(['test'])
    sys.exit(bool(failures))
