from django.test import TestCase
from django.urls import reverse
from accounts.models import UserProfile


class RegisterViewTest(TestCase):
    def test_register_user(self):
        """Test uspesne registrace.
        """

        registration_data = {
            'first_name': 'Honza',
            'last_name': 'Novák',
            'email': 'jenda.novak@seznam.cz',
            'phone': '00420777888999',
            'username': 'jendajeborec',
            'password': 'TotoJeSuperHeslo123!',
            'password_confirm': 'TotoJeSuperHeslo123!',
        }

        response = self.client.post(reverse('register'), data=registration_data)

        self.assertRedirects(response, reverse('login'))

        self.assertTrue(UserProfile.objects.filter(username='jendajeborec').exists())

        messages = list(response.wsgi_request._messages)
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Registrace proběhla úspěšně. Nyní se můžete přihlásit.")

    def test_register_user_invalid_passwords(self):
        """Test selhání registrace při ruznych heslech.
        """
        invalid_data = {
            'first_name': 'Honza',
            'last_name': 'Novák',
            'email': 'jenda.novak@seznam.cz',
            'phone': '00420777888999',
            'username': 'jendajeborec',
            'password': 'TotoJeSuperHeslo123!',
            'password_confirm': 'TotoJeSpatneHeslo',
        }

        response = self.client.post(reverse('register'), data=invalid_data)

        self.assertEqual(response.status_code, 200)

        self.assertContains(response, 'Hesla se neshodují')

        self.assertFalse(UserProfile.objects.filter(username='jendajeborec').exists())

    def test_register_user_duplicate_username(self):
        """Test selhání registrace při duplicitním uživatelském jménu.
        """

        UserProfile.objects.create(username='jendajeborec', email='JenadaNovak@seznam.cz')

        duplicate_user_data = {
            'first_name': 'Honza',
            'last_name': 'Novak',
            'email': 'JendaJinyEmail@seznam.cz',
            'phone': '00420777888999',
            'username': 'jendajeborec',
            'password': 'UltraSuperSilneHeslo123!',
            'password_confirm': 'UltraSuperSilneHeslo123!',
        }

        response = self.client.post(reverse('register'), data=duplicate_user_data)

        self.assertEqual(response.status_code, 200)

        self.assertContains(response, 'Toto uživatelské jméno již existuje')

        self.assertEqual(UserProfile.objects.filter(username='jendajeborec').count(), 1)


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

        response = self.client.post(reverse('login'), data=login_data)

        self.assertRedirects(response, reverse('home'))

        self.assertTrue('_auth_user_id' in self.client.session)

    def test_login_invalid_password(self):
        """Přihlášení pod nesprávným heslem.
        """
        login_data = {
            'username': 'testuser',
            'password': 'NezbedneHeslo!@#',
        }

        response = self.client.post(reverse('login'), data=login_data)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Neplatné uživatelské jméno nebo heslo.')

        self.assertFalse('_auth_user_id' in self.client.session)

    def test_login_nonexistent_user(self):
        """Přihlášení neexistujícího uživatele.
        """
        login_data = {
            'username': 'neexistujiciuzivatel',
            'password': 'TestHesl123!',
        }

        response = self.client.post(reverse('login'), data=login_data)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Neplatné uživatelské jméno nebo heslo.')

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

        self.client.login(username='testuser', password='TestPassword123!')

        response = self.client.get(reverse('logout'))

        self.assertRedirects(response, reverse('login'))

        self.assertFalse('_auth_user_id' in self.client.session)

    def test_logout_not_logged_in(self):
        """Presmerovani odhlaseneho uživatele.
        """
        response = self.client.get(reverse('logout'))

        self.assertRedirects(response, reverse('login'))
