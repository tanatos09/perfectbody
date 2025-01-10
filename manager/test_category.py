from django.test import TestCase
from django.urls import reverse
from accounts.models import UserProfile  # Používáme vlastní model uživatele
from products.models import Category, Product, Producer


class AddCategoryTest(TestCase):
    def setUp(self):
        self.admin_user = UserProfile.objects.create_superuser(
            username="admin", password="password", email="admin@seznam.com"
        )
        self.client.login(username="admin", password="password")

        self.category = Category.objects.create(
            category_name="TestCategory",
            category_description="Test category.",
        )

        self.producer = Producer.objects.create(
            producer_name="TestProducer",
            producer_description="This is a test producer.",
        )
    def test_add_category(self):
        new_category_data = {
            'category_name': 'NewCategory',
            'category_description': 'Test description',
        }

        response = self.client.post(reverse('add_category'), new_category_data)

        self.assertEqual(response.status_code, 302)

        self.assertTrue(Category.objects.filter(category_name='NewCategory').exists())

        category = Category.objects.get(category_name='NewCategory')
        self.assertEqual(category.category_description, 'Test description')

    def test_empty_categories(self):
        empty_category = Category.objects.create(
            category_name="EmptyCategory",
            category_description="Category without products",
        )

        response = self.client.get(reverse('empty_categories'))

        self.assertContains(response, "EmptyCategory")

    def test_add_product_invalid_category(self):
        invalid_product_data = {
            'product_name': 'InvalidProduct',
            'product_short_description': 'Short description',
            'product_long_description': 'Long description',
            'price': 100,
            'category': 999,
            'producer': self.producer.pk,
            'stock_availability': 10,
        }

        response = self.client.post(reverse('add_product'), invalid_product_data)

        self.assertNotEqual(response.status_code, 302)

        self.assertFalse(Product.objects.filter(product_name='InvalidProduct').exists())



class EditCategoryTest(TestCase):
    def setUp(self):
        self.admin_user = UserProfile.objects.create_superuser(
            username="admin", password="password", email="admin@seznam.com"
        )
        self.client.login(username="admin", password="password")

        self.category = Category.objects.create(
            category_name="TestCategory",
            category_description="This is a test category.",
        )

    def test_edit_category(self):
        updated_category_data = {
            'category_name': 'UpdatedCategory',
            'category_description': 'Updated description',
        }

        response = self.client.post(reverse('edit_category', args=[self.category.pk]), updated_category_data)

        self.assertEqual(response.status_code, 302)

        self.category.refresh_from_db()
        self.assertEqual(self.category.category_name, 'UpdatedCategory')
        self.assertEqual(self.category.category_description, 'Updated description')

    def test_edit_category_no_changes(self):
        original_data = {
            'category_name': self.category.category_name,
            'category_description': self.category.category_description,
        }

        response = self.client.post(reverse('edit_category', args=[self.category.pk]), original_data)

        self.assertEqual(response.status_code, 302)

        self.category.refresh_from_db()
        self.assertEqual(self.category.category_name, original_data['category_name'])
        self.assertEqual(self.category.category_description, original_data['category_description'])

    def test_edit_category_missing_name(self):
        incomplete_data = {
            'category_name': '',
            'category_description': 'Updated description',
        }

        response = self.client.post(reverse('edit_category', args=[self.category.pk]), incomplete_data)

        self.assertNotEqual(response.status_code, 302)

        self.category.refresh_from_db()
        self.assertEqual(self.category.category_name, 'TestCategory')
        self.assertEqual(self.category.category_description, 'This is a test category.')

    def test_edit_category_to_duplicate_name(self):
        Category.objects.create(
            category_name="ExistingCategory",
            category_description="Another category.",
        )

        duplicate_data = {
            'category_name': 'ExistingCategory',
            'category_description': 'Updated description',
        }

        response = self.client.post(reverse('edit_category', args=[self.category.pk]), duplicate_data)

        self.assertNotEqual(response.status_code, 302)

        self.category.refresh_from_db()
        self.assertEqual(self.category.category_name, 'TestCategory')


class DeleteCategoryTest(TestCase):
    def setUp(self):
        self.admin_user = UserProfile.objects.create_superuser(
            username="admin", password="password", email="admin@seznam.com"
        )
        self.client.login(username="admin", password="password")

        self.category = Category.objects.create(
            category_name="CategoryToDelete",
            category_description="This category will be deleted.",
        )

    def test_delete_category(self):
        response = self.client.post(reverse('delete_category', args=[self.category.pk]))

        self.assertEqual(response.status_code, 302)

        self.assertFalse(Category.objects.filter(pk=self.category.pk).exists())


class AddDuplicateCategoryTest(TestCase):
    def setUp(self):
        self.admin_user = UserProfile.objects.create_superuser(
            username="admin", password="password", email="admin@seznam.com"
        )
        self.client.login(username="admin", password="password")

        self.category = Category.objects.create(
            category_name="DuplicateCategory",
            category_description="This is the original category.",
        )

    def test_add_duplicate_category(self):
        duplicate_category_data = {
            'category_name': 'DuplicateCategory',
            'category_description': 'A duplicate category.',
        }

        response = self.client.post(reverse('add_category'), duplicate_category_data)

        self.assertNotEqual(response.status_code, 302)

        self.assertEqual(Category.objects.filter(category_name='DuplicateCategory').count(), 1)

    def test_add_category_missing_fields(self):
        response = self.client.post(reverse('add_category'), {
            'category_description': 'Category without a name.',
        })

        self.assertNotEqual(response.status_code, 302)

        self.assertFalse(Category.objects.filter(category_description='Category without a name.').exists())




class DeleteNonexistentCategoryTest(TestCase):
    def setUp(self):
        self.admin_user = UserProfile.objects.create_superuser(
            username="admin", password="password", email="admin@seznam.com"
        )
        self.client.login(username="admin", password="password")

    def test_delete_nonexistent_category(self):
        nonexistent_id = 999
        response = self.client.post(reverse('delete_category', args=[nonexistent_id]))

        self.assertEqual(response.status_code, 404)


class UnauthorizedAccessTest(TestCase):
    def setUp(self):
        self.regular_user = UserProfile.objects.create_user(
            username="user", password="password", email="user@seznam.com"
        )

        self.admin_user = UserProfile.objects.create_superuser(
            username="admin", password="password", email="admin@seznam.com"
        )

        self.category = Category.objects.create(
            category_name="TestCategory",
            category_description="This is a test category.",
        )

    def test_unauthenticated_access(self):
        response = self.client.post(reverse('add_category'), {
            'category_name': 'UnauthenticatedCategory',
            'category_description': 'Description for unauthenticated access.'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith(reverse('login')))

    def test_unauthorized_access(self):
        self.client.login(username="user", password="password")

        response = self.client.post(reverse('delete_category', args=[self.category.pk]))

        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith(reverse('login')))