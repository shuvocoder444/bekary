"""
Comprehensive Automated Test Suite for DHAT Boilerplate
Tests:
1. Health Check Endpoint
2. Dynamic Base Template Pattern (Single-Template Full vs HTMX Partial)
3. Authentication Flow (Standard & HTMX Redirects)
4. Site Settings CRUD & HTMX Out-Of-Band (OOB) Toasts & Logo Swap
5. Static & Environment Configuration
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
        self.assertIn('ক্যালেন্ডার ও সিডিউল', content)

    def test_htmx_request_returns_only_partial_content(self):
        """HTMX boosted request must render only page content without duplicate base.html shell."""
        response = self.client.get(reverse('calendar'), HTTP_HX_REQUEST='true')
        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')

        # Must contain page specific content
        self.assertIn('ক্যালেন্ডার ও সিডিউল', content)

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
        self.assertContains(response, 'অ্যাকাউন্টের তথ্য সঠিক নয়')

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
        self.assertIn('সাইট সেটিংস সফলভাবে আপডেট করা হয়েছে!', content)

        # 2. Rule verification: Targeted sidebar logo swap
        self.assertIn('hx-swap-oob="outerHTML:#sidebar-logo"', content)

        # 3. Database persistence
        self.setting.refresh_from_db()
        self.assertEqual(self.setting.site_name, 'DHAT Enterprise System')


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
