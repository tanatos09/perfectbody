from django.test import TestCase
from django.urls import reverse

from accounts.models import UserProfile
from products.models import Product, Producer, Category


class ProductTest(TestCase):
    def setUp(self):
        self.admin_user = UserProfile.objects.create_superuser(
            username="admin", password="password", email="admin@seznam.com"
        )
        self.client.login(username="admin", password="password")

        self.category = Category.objects.create(
            category_name="TestCategory",
            category_description="This is a test category.",
        )
        self.producer = Producer.objects.create(
            producer_name="TestProducer",
            producer_description="This is a test producer.",
        )

        self.product = Product.objects.create(
            product_name="TestProduct",
            product_short_description="Short description",
            product_long_description="Long description",
            price=100,
            category=self.category,
            producer=self.producer,
            stock_availability=10,
            product_type="merchantdise",
        )

    def test_add_product(self):
        new_product_data = {
            'product_name': 'NewProduct',
            'product_short_description': 'Short description',
            'product_long_description': 'Long description',
            'price': 200,
            'category': self.category.pk,
            'producer': self.producer.pk,
            'stock_availability': 15,
            'product_type': 'merchantdise',
        }

        response = self.client.post(reverse('add_product'), new_product_data)

        self.assertEqual(response.status_code, 302)

        self.assertTrue(Product.objects.filter(product_name='NewProduct').exists())

    def test_edit_product(self):
        updated_product_data = {
            'product_name': 'UpdatedProduct',
            'product_short_description': 'Updated short description',
            'product_long_description': 'Updated long description',
            'price': 300,
            'category': self.category.pk,
            'producer': self.producer.pk,
            'stock_availability': 5,
            'product_type': 'merchantdise',
        }

        response = self.client.post(reverse('edit_product', args=[self.product.pk]), updated_product_data)

        self.assertEqual(response.status_code, 302)

        self.product.refresh_from_db()
        self.assertEqual(self.product.product_name, 'UpdatedProduct')

    def test_delete_product(self):
        response = self.client.post(reverse('delete_product', args=[self.product.pk]))

        self.assertEqual(response.status_code, 302)

        self.assertFalse(Product.objects.filter(pk=self.product.pk).exists())

    def test_unauthorized_access(self):
        regular_user = UserProfile.objects.create_user(
            username="user", password="password", email="user@seznam.com"
        )
        self.client.login(username="user", password="password")

        response = self.client.post(reverse('add_product'), {
            'product_name': 'UnauthorizedProduct',
            'product_short_description': 'Short description',
            'product_long_description': 'Long description',
            'price': 200,
            'category': self.category.pk,
            'producer': self.producer.pk,
            'stock_availability': 15,
            'product_type': 'merchantdise',
        })

        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith(reverse('login')))


class ServiceTest(TestCase):
    def setUp(self):
        self.admin_user = UserProfile.objects.create_superuser(
            username="admin", password="password", email="admin@seznam.com"
        )
        self.client.login(username="admin", password="password")

        self.category = Category.objects.create(
            category_name="ServiceCategory",
            category_description="This is a test category for services.",
        )

        self.service = Product.objects.create(
            product_name="TestService",
            product_short_description="Short description of service",
            product_long_description="Long description of service",
            price=500,
            category=self.category,
            product_type="service",
            producer=None,
            stock_availability=0,
        )

    def test_add_service(self):
        new_service_data = {
            'product_name': 'NewService',
            'product_short_description': 'Short description of new service',
            'product_long_description': 'Long description of new service',
            'price': 1000,
            'category': self.category.pk,
            'product_type': 'service',
        }

        response = self.client.post(reverse('add_service'), new_service_data)

        self.assertEqual(response.status_code, 302)

        self.assertTrue(Product.objects.filter(product_name='NewService').exists())

    def test_edit_service(self):
        updated_service_data = {
            'product_name': 'UpdatedService',
            'product_short_description': 'Updated short description',
            'product_long_description': 'Updated long description',
            'price': 700,
            'category': self.category.pk,
            'product_type': 'service',
        }

        response = self.client.post(reverse('edit_service', args=[self.service.pk]), updated_service_data)

        self.assertEqual(response.status_code, 302)

        self.service.refresh_from_db()
        self.assertEqual(self.service.product_name, 'UpdatedService')

    def test_delete_service(self):
        response = self.client.post(reverse('delete_service', args=[self.service.pk]))

        self.assertEqual(response.status_code, 302)

        self.assertFalse(Product.objects.filter(pk=self.service.pk).exists())

    def test_unauthorized_access(self):
        regular_user = UserProfile.objects.create_user(
            username="user", password="password", email="user@seznam.com"
        )
        self.client.login(username="user", password="password")

        response = self.client.post(reverse('add_service'), {
            'product_name': 'UnauthorizedService',
            'product_short_description': 'Short description',
            'product_long_description': 'Long description',
            'price': 1000,
            'category': self.category.pk,
            'product_type': 'service',
        })

        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith(reverse('login')))
