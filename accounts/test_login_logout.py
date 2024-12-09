from django.test import TestCase
from django.urls import reverse
from accounts.models import UserProfile


class LoginViewTest(TestCase):
    def setUp(self):
        """Testovací uživatel.
        """
        self.user = UserProfile.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='TestPassword123!'
        )

    def test_login_success(self):
        """Uspěšné přihlášení."""
        login_data = {
            'username': 'testuser',
            'password': 'TestPassword123!',
        }

        # pozadavek POST
        response = self.client.post(reverse('login'), data=login_data)

        # kontrola presmerovani na 'home'
        self.assertRedirects(response, reverse('home'))

        # overeni prihlaseni uzivatele - session obsahuje uzivatelovo ID
        self.assertTrue('_auth_user_id' in self.client.session)

    def test_login_invalid_password(self):
        """Přihlášení pod nesprávným heslem.
        """
        login_data = {
            'username': 'testuser',
            'password': 'NezbedneHeslo!@#',
        }

        # POST pozadavek
        response = self.client.post(reverse('login'), data=login_data)

        # kontrola vraceni kodu 200
        self.assertEqual(response.status_code, 200)
        # kontrola chybove hlasky
        self.assertContains(response, 'Neplatné uživatelské jméno nebo heslo.')

        # kontrola ze uzivatel neni prihlaseny
        self.assertFalse('_auth_user_id' in self.client.session)

    def test_login_nonexistent_user(self):
        """Přihlášení neexistujícího uživatele.
        """
        login_data = {
            'username': 'neexistujiciuzivatel',
            'password': 'TestHesl123!',
        }
        # simulace POST
        response = self.client.post(reverse('login'), data=login_data)

        # vraceni hlasky 200
        self.assertEqual(response.status_code, 200)
        #kontrola chybove hlasky
        self.assertContains(response, 'Neplatné uživatelské jméno nebo heslo.')

        # uzivatel neni prihlasen
        self.assertFalse('_auth_user_id' in self.client.session)

    def test_login_redirect_authenticated_user(self):
        """Prihlaseny uzivatel se snazi opetovne prihlasit.
        """

        self.client.login(username='testuser', password='TestPassword123!')

        response = self.client.get(reverse('login'))


class LogoutViewTest(TestCase):
    def setUp(self):
        """Testovaci uzivatel.
        """

        self.user = UserProfile.objects.create_user(
            username='testuser',
            email='testuser@seznam.cz',
            password='TestPassword123!'
        )

    def test_logout_success(self):
        """Test úspěšného odhlášení.
        """

        # prihlasi uzivatele
        self.client.login(username='testuser', password='TestPassword123!')

        # GET pozadavek pro odhlaseni
        response = self.client.get(reverse('logout'))

        # overeni ze pri odhlaseni se vratime na 'login'
        self.assertRedirects(response, reverse('login'))

        # kontola odhlaseneho uzivatele
        self.assertFalse('_auth_user_id' in self.client.session)

    def test_logout_not_logged_in(self):
        """Odhlaseni neprihlaseneho uživatele.
        """
        # GET pozadavek na odhlaseni
        response = self.client.get(reverse('logout'))

        # presmerovani na 'login'
        self.assertRedirects(response, reverse('login'))
