from django.test import TestCase
from django.urls import reverse
from accounts.models import UserProfile

class UserManagementTest(TestCase):
    def setUp(self):
        # Administrátor
        self.admin_user = UserProfile.objects.create_superuser(
            username="admin",
            password="password",
            email="admin@seznam.com",
            first_name="AdminFirstName",
            last_name="AdminLastName",
        )
        self.client.login(username="admin", password="password")

        # Běžný uživatel
        self.user = UserProfile.objects.create_user(
            username="user",
            password="password",
            email="user@seznam.com",
            first_name="UserFirstName",
            last_name="UserLastName",
        )

    def test_update_user(self):
        updated_user_data = {
            'first_name': 'UpdatedFirstName',
            'last_name': 'UpdatedLastName',
            'email': self.user.email,
        }

        response = self.client.post(reverse('edit_user', args=[self.user.pk]), updated_user_data)

        self.assertEqual(response.status_code, 302)

        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'UpdatedFirstName')
        self.assertEqual(self.user.last_name, 'UpdatedLastName')

    def test_promote_user_to_admin(self):
        promote_to_admin_data = {
            'first_name': self.user.first_name,
            'last_name': self.user.last_name,
            'email': self.user.email,
            'is_staff': True,
        }

        response = self.client.post(reverse('edit_user', args=[self.user.pk]), promote_to_admin_data)

        if response.status_code == 200:
            print("Form errors:", response.context['form'].errors)

        self.assertEqual(response.status_code, 302)

        self.user.refresh_from_db()
        self.assertTrue(self.user.is_staff)

    def test_promote_user_to_superadmin(self):
        promote_to_superadmin_data = {
            'first_name': self.user.first_name,
            'last_name': self.user.last_name,
            'email': self.user.email,
            'is_staff': True,
            'is_superuser': True,
        }

        response = self.client.post(reverse('edit_user', args=[self.user.pk]), promote_to_superadmin_data)

        self.assertEqual(response.status_code, 302)

        self.user.refresh_from_db()
        self.assertTrue(self.user.is_staff)
        self.assertTrue(self.user.is_superuser)

    def test_unauthorized_promotion(self):
        self.client.logout()
        self.client.login(username="user", password="password")

        unauthorized_promotion_data = {
            'first_name': self.user.first_name,
            'last_name': self.user.last_name,
            'email': self.user.email,
            'is_staff': True,
            'is_superuser': True,
        }

        response = self.client.post(reverse('edit_user', args=[self.user.pk]), unauthorized_promotion_data)

        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith(reverse('login')))

        self.user.refresh_from_db()
        self.assertFalse(self.user.is_staff)
        self.assertFalse(self.user.is_superuser)

    def test_regular_user_access_admin(self):
        self.client.logout()
        self.client.login(username="user", password="password")

        response = self.client.get(reverse('dashboard'))

        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith(reverse('login')))

    def test_delete_user(self):
        response = self.client.post(reverse('delete_user', args=[self.user.pk]))

        self.assertEqual(response.status_code, 302)

        self.assertFalse(UserProfile.objects.filter(pk=self.user.pk).exists())


