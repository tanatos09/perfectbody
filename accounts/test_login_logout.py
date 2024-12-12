from django.test import TestCase
from django.urls import reverse
from accounts.models import UserProfile


class LoginViewTest(TestCase):
    def setUp(self):
        """test user.
        """
        self.user = UserProfile.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='TestPassword123!'
        )

    def test_login_success(self):
        """successful login."""
        login_data = {
            'username': 'testuser',
            'password': 'TestPassword123!',
        }

        response = self.client.post(reverse('login'), data=login_data)
        self.assertRedirects(response, reverse('home'))
        self.assertTrue('_auth_user_id' in self.client.session)

    def test_login_invalid_password(self):
        """logging in with an incorrect password"""
        login_data = {
            'username': 'testuser',
            'password': 'NezbedneHeslo!@#',
        }

        response = self.client.post(reverse('login'), data=login_data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Neplatné uživatelské jméno nebo heslo.')
        self.assertFalse('_auth_user_id' in self.client.session)

    def test_login_nonexistent_user(self):
        """login - non-exist user"""
        login_data = {
            'username': 'neexistujiciuzivatel',
            'password': 'TestHesl123!',
        }

        response = self.client.post(reverse('login'), data=login_data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Neplatné uživatelské jméno nebo heslo.')
        self.assertFalse('_auth_user_id' in self.client.session)

    def test_login_redirect_authenticated_user(self):
        """the logged user trying to log in again.
        """
        self.client.login(username='testuser', password='TestPassword123!')

        response = self.client.get(reverse('login'))
        self.assertRedirects(response, reverse('home'))


class LogoutViewTest(TestCase):
    def setUp(self):
        """test user.
        """

        self.user = UserProfile.objects.create_user(
            username='testuser',
            email='testuser@seznam.cz',
            password='TestPassword123!'
        )

    def test_logout_success(self):
        """sucessful logout"""

        self.client.login(username='testuser', password='TestPassword123!')
        response = self.client.get(reverse('logout'))
        self.assertRedirects(response, reverse('login'))
        self.assertFalse('_auth_user_id' in self.client.session)

    def test_logout_not_logged_in(self):
        """logging out a user - not logget in"""
        response = self.client.get(reverse('logout'))
        self.assertRedirects(response, reverse('login'))
