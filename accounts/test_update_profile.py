from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class BaseTestCase(TestCase):
    def assertRedirectsToLogin(self, response, next_url):
        self.assertRedirects(response, reverse('login') + f"?next={next_url}")


class EditProfileTest(BaseTestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='TestovaciUzivatel',
            email='testovaci.uzivate@seznam.cz',
            password='bezpecneHesl0',
            first_name='Test',
            last_name='Uzivatel',
            preferred_channel='EMAIL',
        )
        self.edit_profile_url = reverse('edit_profile')

    def test_edit_not_logged_user(self):
        response = self.client.get(self.edit_profile_url)
        self.assertRedirectsToLogin(response, self.edit_profile_url)

    def test_edit_logged_user(self):
        self.client.login(username='TestovaciUzivatel', password='bezpecneHesl0')
        updated_data = {
            'username': 'UpravenyUzivatel',
            'email': 'updated.email@seznam.cz',
            'first_name': 'Upraveny',
            'last_name': 'Uzivatel',
            'preferred_channel': 'PHONE',
        }
        response = self.client.post(self.edit_profile_url, updated_data)
        self.assertRedirects(response, reverse('profile'))

        self.user.refresh_from_db()
        self.assertEqual(self.user.username, 'UpravenyUzivatel')
        self.assertEqual(self.user.email, 'updated.email@seznam.cz')
        self.assertEqual(self.user.first_name, 'Upraveny')
        self.assertEqual(self.user.last_name, 'Uzivatel')
        self.assertEqual(self.user.preferred_channel, 'PHONE')

    def test_edit_invalid_data(self):
        self.client.login(username='TestovaciUzivatel', password='bezpecneHesl0')
        invalid_data = {
            'username': 'TestovaciUzivatel',
            'email': 'testovaci.uzivatel.cz',
            'preferred_channel': 'EMAIL',
        }
        response = self.client.post(self.edit_profile_url, invalid_data)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Údaje nejsou platné, zkuste to znovu')  # Chybová zpráva
        self.assertIn('email', response.context['form'].errors)  # Pole 'email' má chybu
        self.assertEqual(response.context['form'].errors['email'],['Zadejte platnou e-mailovou adresu.'])  # Kontrola textu chyby


class ProfileViewTest(BaseTestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='TestovaciUzivatel',
            email='testovaci.uzivate@seznam.cz',
            password='bezpecneHesl0',
        )
        self.profile_url = reverse('profile')

    def test_profile_view_not_logged_user(self):
        response = self.client.get(self.profile_url)
        self.assertRedirectsToLogin(response, self.profile_url)

    def test_profile_view_logged_user(self):
        self.client.login(username='TestovaciUzivatel', password='bezpecneHesl0')
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'TestovaciUzivatel')
        self.assertTemplateUsed(response, 'profile.html')
