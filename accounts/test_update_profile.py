from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class EditProfileTest(TestCase):
    def setUp(self):
        '''test user'''
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
        '''login - not-logged user'''
        response = self.client.get(self.edit_profile_url)
        self.assertRedirects(response, f"{reverse('login')}?next={self.edit_profile_url}")

    def test_edit_logged_user(self):
        '''login - logged user'''
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
        '''edit profile - entered incorrect data'''
        self.client.login(username='TestovaciUzivatel', password='bezpecneHesl0')
        invalid_data = {
            'username': 'TestovaciUzivatel',
            'email': 'testovaci.uzivatel.cz',
            'preferred_channel': 'EMAIL',
        }
        response = self.client.post(self.edit_profile_url, invalid_data)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Údaje nejsou platné, zkuste to znovu')
        self.assertIn('email', response.context['form'].errors)
        self.assertEqual(response.context['form'].errors['email'], ['Zadejte platnou e-mailovou adresu.'])


class ProfileViewTest(TestCase):
    def setUp(self):
        '''test user'''
        self.user = get_user_model().objects.create_user(
            username='TestovaciUzivatel',
            email='testovaci.uzivate@seznam.cz',
            password='bezpecneHesl0',
        )
        self.profile_url = reverse('profile')

    def test_profile_view_not_logged_user(self):
        '''view profile - not logged'''
        response = self.client.get(self.profile_url)
        self.assertRedirects(response, f"{reverse('login')}?next={self.profile_url}")

    def test_profile_view_logged_user(self):
        '''view profile - logged'''
        self.client.login(username='TestovaciUzivatel', password='bezpecneHesl0')
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'TestovaciUzivatel')
        self.assertTemplateUsed(response, 'profile.html')


class ChangePasswordTest(TestCase):
    def setUp(self):
        '''test user'''
        self.user = get_user_model().objects.create_user(
            username='TestovaciUzivatel',
            email='testovaci.uzivate@seznam.cz',
            password='PuvodniHeslo123'
        )
        self.change_password_url = reverse('change_password')
        self.client.login(username='TestovaciUzivatel', password='PuvodniHeslo123')

    def test_change_password_success(self):
        '''password has been changed'''
        response = self.client.post(self.change_password_url, {
            'old_password': 'PuvodniHeslo123',
            'new_password': 'NoveHeslo123',
            'confirm_password': 'NoveHeslo123',
        })
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('NoveHeslo123'))
        self.assertRedirects(response, reverse('profile'))

    def test_change_password_wrong_old(self):
        '''password change failed - wrong old password'''
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
        '''password change failed - different new passwords'''
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


