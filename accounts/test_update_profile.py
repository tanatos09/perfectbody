from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.contrib.messages import get_messages
from django.test import TestCase
from django.urls import reverse

from accounts.models import Address, UserProfile


class ChangePasswordTest(TestCase):
    def setUp(self):
        """Vytvoření testovacího uživatele"""
        self.user = get_user_model().objects.create_user(
            username='TestovaciUzivatel',
            email='testovaci.uzivate@seznam.cz',
            password='PuvodniHeslo123'
        )
        self.change_password_url = reverse('change_password')
        self.client.login(username='TestovaciUzivatel', password='PuvodniHeslo123')

    def test_change_password_success(self):
        """Heslo bylo úspěšně změněno"""
        response = self.client.post(self.change_password_url, {
            'old_password': 'PuvodniHeslo123',
            'new_password': 'NoveHeslo123',
            'confirm_password': 'NoveHeslo123',
        })
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('NoveHeslo123'))
        self.assertRedirects(response, reverse('profile'))

    def test_change_password_wrong_old(self):
        """Změna hesla selhala - špatné staré heslo"""
        response = self.client.post(self.change_password_url, {
            'old_password': 'SpatneHeslo123',
            'new_password': 'NoveHeslo123',
            'confirm_password': 'NoveHeslo123',
        })
        self.user.refresh_from_db()

        self.assertFalse(self.user.check_password('NoveHeslo123'))
        self.assertTrue(self.user.check_password('PuvodniHeslo123'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Heslo nebylo změněno')

    def test_change_password_no_match(self):
        """Změna hesla selhala - nová hesla se neshodují"""
        response = self.client.post(self.change_password_url, {
            'old_password': 'PuvodniHeslo123',
            'new_password': 'NoveHeslo123',
            'confirm_password': 'JineHeslo123',
        })

        self.user.refresh_from_db()

        self.assertFalse(self.user.check_password('NoveHeslo123'))
        self.assertFalse(self.user.check_password('JineHeslo123'))
        self.assertTrue(self.user.check_password('PuvodniHeslo123'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Heslo nebylo změněno')

    def test_change_password_empty_new_password(self):
        response = self.client.post(self.change_password_url, {
            'old_password': 'PuvodniHeslo123',
            'new_password': '',
            'confirm_password': '',
        })

        self.user.refresh_from_db()

        self.assertTrue(self.user.check_password('PuvodniHeslo123'))

        self.assertContains(response, 'Heslo nebylo změněno')


class EditProfileTest(TestCase):
    def setUp(self):
        self.user = UserProfile.objects.create_user(
            username='testuser',
            password='password123',
            first_name='OldFirstName',
            last_name='OldLastName',
            email='old@example.com',
            phone='123456789',
        )

        self.client.login(username='testuser', password='password123')
        self.url = reverse('edit_profile')
        self.client.login(username='testuser', password='password123')
        self.url = reverse('edit_profile')
        self.address = Address.objects.create(
            user=self.user,
            first_name='OldFirstName',
            last_name='OldLastName',
            street='OldStreet',
            street_number='123',
            city='OldCity',
            postal_code='12345',
            country='OldCountry',
            email='old@example.com'
        )
        self.client.login(username='testuser', password='password123')
        self.url = reverse('edit_profile')

    def test_edit_address(self):
        post_data = {
            'form_type': 'shipping_form',
            'shipping-first_name': 'NewFirstName',
            'shipping-last_name': 'NewLastName',
            'shipping-street': 'NewStreet',
            'shipping-street_number': '456',
            'shipping-city': 'NewCity',
            'shipping-postal_code': '54321',
            'shipping-country': 'NewCountry',
            'shipping-email': 'new@example.com',
        }
        response = self.client.post(self.url, post_data)

        self.address.refresh_from_db()

        self.assertEqual(self.address.first_name, 'NewFirstName')
        self.assertEqual(self.address.last_name, 'NewLastName')
        self.assertEqual(self.address.street, 'NewStreet')
        self.assertEqual(self.address.street_number, '456')
        self.assertEqual(self.address.city, 'NewCity')
        self.assertEqual(self.address.postal_code, '54321')
        self.assertEqual(self.address.country, 'NewCountry')
        self.assertEqual(self.address.email, 'new@example.com')

        messages = list(response.wsgi_request._messages)
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Adresa byla úspěšně změněna.")

    def test_edit_personal_details(self):
        post_data = {
            'form_type': 'user_form',
            'username': 'testuser',
            'first_name': 'NewFirstName',
            'last_name': 'NewLastName',
            'email': 'new@example.com',
            'phone': '987654321',
            'avatar': 'http://example.com/new_avatar.png',
            'preferred_channel': 'PHONE',
        }
        response = self.client.post(self.url, post_data)

        self.assertEqual(response.status_code, 200)

        self.user.refresh_from_db()

        self.assertEqual(self.user.first_name, 'NewFirstName')
        self.assertEqual(self.user.last_name, 'NewLastName')
        self.assertEqual(self.user.email, 'new@example.com')
        self.assertEqual(self.user.phone, '987654321')
        self.assertEqual(self.user.avatar, 'http://example.com/new_avatar.png')
        self.assertEqual(self.user.preferred_channel, 'PHONE')

        messages = list(response.wsgi_request._messages)
        self.assertEqual(len(messages), 1, "Očekával se jeden message")
        self.assertEqual(str(messages[0]), "Osobní údaje byly úspěšně změněny.")

    def test_edit_address_invalid_data(self):
        post_data = {
            'form_type': 'shipping_form',
            'shipping-first_name': '',
            'shipping-last_name': '',
            'shipping-email': 'invalid-email',
        }
        response = self.client.post(self.url, post_data)

        self.address.refresh_from_db()
        self.assertNotEqual(self.address.first_name, '')
        self.assertNotEqual(self.address.last_name, '')

        messages = list(response.wsgi_request._messages)
        self.assertGreater(len(messages), 0)
        self.assertIn("first_name: Toto pole je třeba vyplnit.", [str(m) for m in messages])
        self.assertIn("last_name: Toto pole je třeba vyplnit.", [str(m) for m in messages])
        self.assertIn("email: Zadejte platnou e-mailovou adresu.", [str(m) for m in messages])

    def test_edit_personal_details_duplicate_email(self):
        UserProfile.objects.create_user(
            username='anotheruser',
            email='duplicate@example.com',
            password='password123'
        )

        post_data = {
            'form_type': 'user_form',
            'username': 'testuser',
            'first_name': 'NewFirstName',
            'last_name': 'NewLastName',
            'email': 'duplicate@example.com',
            'phone': '987654321',
            'avatar': 'http://example.com/new_avatar.png',
            'preferred_channel': 'PHONE',
        }
        response = self.client.post(self.url, post_data)

        self.assertEqual(response.status_code, 200)

        self.user.refresh_from_db()
        self.assertNotEqual(self.user.email, 'duplicate@example.com')

        self.assertContains(response, "Tento email již existuje.")

    def test_phone_with_invalid_characters(self):
        """Telefon obsahující nepovolené znaky by měl selhat"""
        invalid_phone_data = {
            "form_type": "user_form",
            "username": "testuser",
            "first_name": "NewFirstName",
            "last_name": "NewLastName",
            "email": "new@example.com",
            "phone": "123ABC@!#",
        }
        response = self.client.post(self.url, invalid_phone_data)
        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        self.assertNotEqual(self.user.phone, "123ABC@!#")
        self.assertContains(response, "Telefonní číslo může obsahovat pouze číslice.")

    def test_unauthorized_user_access(self):
        """Nepřihlášený uživatel by neměl mít přístup na stránku úpravy profilu"""
        self.client.logout()  # Odhlásíme uživatele
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith(reverse("login")))






