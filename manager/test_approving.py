from django.test import TestCase
from django.urls import reverse
from accounts.models import UserProfile, TrainersServices
from products.models import Product, Category

class ApprovalTest(TestCase):
    def setUp(self):
        self.admin_user = UserProfile.objects.create_superuser(
            username="admin", password="password", email="admin@seznam.com"
        )
        self.client.login(username="admin", password="password")

        self.category = Category.objects.create(
            category_name="ServiceCategory",
            category_description="Test category.",
        )

        self.trainer = UserProfile.objects.create_user(
            username="trainer",
            password="password",
            email="trainer@seznam.com",
            is_active=True,
            pending_trainer_short_description="Pending short description",
            pending_trainer_long_description="Pending long description",
        )

        self.service = Product.objects.create(
            product_name="TestService",
            product_short_description="Short description",
            product_long_description="Long description",
            price=500,
            category=self.category,
            product_type="service",
            producer=None,
            stock_availability=0,
        )

        self.trainer_service = TrainersServices.objects.create(
            trainer=self.trainer,
            service=self.service,
            trainers_service_description="Service description",
            pending_trainers_service_description="Pending service description",
            is_approved=False,
        )

    def test_approve_trainer_services(self):
        response = self.client.post(reverse('approve_service'), {'service_id': self.trainer_service.pk})

        self.assertEqual(response.status_code, 302)

        self.trainer_service.refresh_from_db()
        self.assertTrue(self.trainer_service.is_approved)

    def test_approve_trainer_short_description(self):
        response = self.client.post(reverse('approve_trainer_content'), {
            'content_type': 'trainer_short_description',
            'content_id': self.trainer.pk,
            'action': 'approve',
        })

        self.assertEqual(response.status_code, 302)

        self.trainer.refresh_from_db()
        self.assertEqual(self.trainer.trainer_short_description, "Pending short description")
        self.assertIsNone(self.trainer.pending_trainer_short_description)

    def test_approve_trainer_long_description(self):
        response = self.client.post(reverse('approve_trainer_content'), {
            'content_type': 'trainer_long_description',
            'content_id': self.trainer.pk,
            'action': 'approve',
        })

        self.assertEqual(response.status_code, 302)

        self.trainer.refresh_from_db()
        self.assertEqual(self.trainer.trainer_long_description, "Pending long description")
        self.assertIsNone(self.trainer.pending_trainer_long_description)

    def test_approve_service_description(self):
        response = self.client.post(reverse('approve_trainer_content'), {
            'content_type': 'service',
            'content_id': self.trainer_service.pk,
            'action': 'approve',
        })

        self.assertEqual(response.status_code, 302)

        self.trainer_service.refresh_from_db()
        self.assertEqual(self.trainer_service.trainers_service_description, "Pending service description")
        self.assertIsNone(self.trainer_service.pending_trainers_service_description)
