from django.test import TestCase
from django.urls import reverse
from accounts.models import UserProfile


class LoginViewTest(TestCase):
    def setUp(self):
        """Create a test user."""
        self.user = UserProfile.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='TestPassword123!'
        )

    def test_login_success(self):
        """Successful login."""
        response = self.client.post(reverse('login'), data={
            'username': 'testuser',
            'password': 'TestPassword123!',
        })
        self.assertRedirects(response, reverse('home'))
        self.assertTrue('_auth_user_id' in self.client.session)

    def test_login_invalid_password(self):
        """Login with incorrect password."""
        response = self.client.post(reverse('login'), data={
            'username': 'testuser',
            'password': 'WrongPassword!',
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Neplatné uživatelské jméno nebo heslo.")
        self.assertFalse('_auth_user_id' in self.client.session)

    def test_login_nonexistent_user(self):
        """Login with a non-existent user."""
        response = self.client.post(reverse('login'), data={
            'username': 'nouser',
            'password': 'TestPassword123!',
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Neplatné uživatelské jméno nebo heslo.")
        self.assertFalse('_auth_user_id' in self.client.session)

    def test_redirect_authenticated_user(self):
        """Redirect an authenticated user trying to access the login page."""
        self.client.login(username='testuser', password='TestPassword123!')
        response = self.client.get(reverse('login'))
        self.assertRedirects(response, reverse('home'))


class LogoutViewTest(TestCase):
    def setUp(self):
        """Create a test user."""
        self.user = UserProfile.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='TestPassword123!'
        )

    def test_logout_success(self):
        """Successful logout."""
        self.client.login(username='testuser', password='TestPassword123!')
        response = self.client.get(reverse('logout'))
        self.assertRedirects(response, reverse('login'))
        self.assertFalse('_auth_user_id' in self.client.session)

    def test_logout_not_logged_in(self):
        """Logout when not logged in."""
        response = self.client.get(reverse('logout'))
        self.assertRedirects(response, reverse('login'))
