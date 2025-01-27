from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.contrib.messages import get_messages
from django.test import TestCase
from django.urls import reverse

from accounts.forms import UserEditForm
from accounts.models import Address, UserProfile, TrainersServices
from products.models import Product, Producer, Category


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
        self.user = get_user_model().objects.create_user(
            username='TestovaciUzivatel',
            email='testovaci.uzivatel@seznam.cz',
            password='Heslo123'
        )
        self.profile_url = reverse('edit_profile')
        self.client.login(username='TestovaciUzivatel', password='Heslo123')

    def test_edit_address_success(self):
        Address.objects.create(
            user=self.user,
            first_name='Test',
            last_name='User',
            street='Test Street',
            street_number='123',
            city='Test City',
            postal_code='12345',
            country='Česká republika',
            email='testovaci.uzivatel@seznam.cz'
        )

        response = self.client.post(self.profile_url, {
            'form_type': 'shipping_form',
            'first_name': 'Nové',
            'last_name': 'Jméno',
            'street': 'Nová Street',
            'street_number': '456',
            'city': 'Nové Město',
            'postal_code': '54321',
            'country': 'Slovensko',
            'email': 'novy.email@seznam.cz',
        })

        updated_address = Address.objects.filter(user=self.user).latest('id')

        self.assertEqual(updated_address.first_name, 'Nové')
        self.assertEqual(updated_address.city, 'Nové Město')
        self.assertRedirects(response, self.profile_url)

    def test_edit_personal_data_success(self):
        response = self.client.post(self.profile_url, {
            'form_type': 'user_form',
            'username': 'NovyUzivatel',
            'first_name': 'NovéJméno',
            'last_name': 'NovéPříjmení',
            'email': 'novy.email@seznam.cz',
            'phone': '123456789',
            'preferred_channel': 'EMAIL',
        })


        if response.status_code == 200:
            print("Form errors (if any):", response.context['user_form'].errors)

        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'NovéJméno')
        self.assertEqual(self.user.preferred_channel, 'EMAIL')
        self.assertRedirects(response, self.profile_url)

    def test_edit_personal_data_invalid_email(self):
        response = self.client.post(self.profile_url, {
            'form_type': 'user_form',
            'username': 'NovyUzivatel',
            'first_name': 'NovéJméno',
            'last_name': 'NovéPříjmení',
            'email': 'nevalidni-email',
            'phone': '123456789',
        })

        self.user.refresh_from_db()

        self.assertNotEqual(self.user.email, 'nevalidni-email')
        self.assertContains(response, 'Zadejte platnou e-mailovou adresu')

    def test_edit_personal_data_existing_email(self):
        get_user_model().objects.create_user(
            username='JinyUzivatel',
            email='existujici.email@seznam.cz',
            password='Heslo123'
        )

        response = self.client.post(self.profile_url, {
            'form_type': 'user_form',
            'username': 'NovyUzivatel',
            'first_name': 'NovéJméno',
            'last_name': 'NovéPříjmení',
            'email': 'existujici.email@seznam.cz',
            'phone': '123456789',
        })

        self.user.refresh_from_db()

        self.assertNotEqual(self.user.email, 'existujici.email@seznam.cz')
        self.assertContains(response, 'Tento email již existuje.')

    def test_edit_personal_data_invalid_phone(self):
        response = self.client.post(self.profile_url, {
            'form_type': 'user_form',
            'username': 'NovyUzivatel',
            'first_name': 'NovéJméno',
            'last_name': 'NovéPříjmení',
            'email': 'novy.email@seznam.cz',
            'phone': 'neplatnýTelefon',
        })

        self.user.refresh_from_db()

        self.assertNotEqual(self.user.phone, 'neplatnýTelefon')
        self.assertContains(response, 'Telefonní číslo může obsahovat pouze číslice.')

    def test_unauthenticated_user_redirect(self):
        self.client.logout()
        response = self.client.get(self.profile_url)
        self.assertRedirects(response, f"{reverse('login')}?next={self.profile_url}")

    def test_invalid_phone_number(self):
        """Chyba při neplatném telefonním čísle"""
        response = self.client.post(self.profile_url, {
            'form_type': 'user_form',
            'username': 'NovyUzivatel',
            'first_name': 'NovéJméno',
            'last_name': 'NovéPříjmení',
            'email': 'novy.email@seznam.cz',
            'phone': 'invalidPhone',  # Neplatné telefonní číslo
            'preferred_channel': 'EMAIL',
        })

        self.user.refresh_from_db()

        self.assertNotEqual(self.user.phone, 'invalidPhone')
        self.assertContains(response, 'Telefonní číslo může obsahovat pouze číslice.')

    def test_duplicate_email(self):
        """Chyba při použití existujícího e-mailu"""
        get_user_model().objects.create_user(
            username='JinyUzivatel',
            email='existujici.email@seznam.cz',
            password='Heslo123'
        )

        response = self.client.post(self.profile_url, {
            'form_type': 'user_form',
            'username': 'NovyUzivatel',
            'first_name': 'NovéJméno',
            'last_name': 'NovéPříjmení',
            'email': 'existujici.email@seznam.cz',
            'phone': '123456789',
            'preferred_channel': 'EMAIL',
        })

        self.user.refresh_from_db()

        self.assertNotEqual(self.user.email, 'existujici.email@seznam.cz')
        self.assertContains(response, 'Tento email již existuje.')

    def test_invalid_address_data(self):
        """Chyba při neplatných datech adresy"""
        response = self.client.post(self.profile_url, {
            'form_type': 'shipping_form',
            'first_name': 'Test',
            'last_name': 'User',
            'street': 'Invalid Street',
            'street_number': '123',
            'city': 'Invalid City',
            'postal_code': 'InvalidPSČ',  # Neplatné PSČ
            'country': 'Česká republika',
            'email': 'test@seznam.cz',
        })

        address_count = Address.objects.filter(user=self.user).count()

        self.assertEqual(address_count, 0)
        self.assertContains(response, 'PSČ musí obsahovat pouze číslice.')

class TrainerProfileTest(TestCase):
    def setUp(self):
        """Příprava testovacího prostředí"""
        # Vytvoření kategorie
        self.category = Category.objects.create(
            category_name="Test Category",
            category_description="Popis testovací kategorie"
        )

        # Vytvoření producenta
        self.producer = Producer.objects.create(producer_name="Test Producer")

        # Vytvoření testovacích produktů (služeb)
        self.service_1 = Product.objects.create(
            product_name="Osobní trénink",
            product_type="service",
            price=500,
            producer=self.producer,
            category=self.category,  # Nastavení kategorie
            product_short_description="Krátký popis služby",
            product_long_description="Dlouhý popis služby",
        )
        self.service_2 = Product.objects.create(
            product_name="Online trénink",
            product_type="service",
            price=300,
            producer=self.producer,
            category=self.category,  # Nastavení kategorie
            product_short_description="Krátký popis služby",
            product_long_description="Dlouhý popis služby",
        )

        # Vytvoření trenéra
        self.trainer = get_user_model().objects.create_user(
            username="TestTrener",
            email="test.trener@seznam.cz",
            password="Heslo123",
            trainer_short_description="Zkušený trenér",
            trainer_long_description="Detailní informace o trenérovi.",
        )

        # Přidání schválených služeb s popisky
        self.service_description_1 = TrainersServices.objects.create(
            trainer=self.trainer,
            service=self.service_1,
            trainers_service_description="Pomoc při osobním tréninku.",
            pending_trainers_service_description="",
        )
        self.service_description_2 = TrainersServices.objects.create(
            trainer=self.trainer,
            service=self.service_2,
            trainers_service_description="Pomoc při online tréninku.",
            pending_trainers_service_description="",
        )

        self.edit_profile_url = reverse("edit_profile")
        self.client.login(username="TestTrener", password="Heslo123")

    def test_invalid_service_description(self):
        response = self.client.post(self.edit_profile_url, {
            "form_type": "service_form",
            f"description_{self.service_description_1.id}": "",
            f"description_{self.service_description_2.id}": "Krátký",
        })

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.edit_profile_url)

        service_1 = TrainersServices.objects.get(id=self.service_description_1.id)
        service_2 = TrainersServices.objects.get(id=self.service_description_2.id)

        self.assertEqual(service_1.pending_trainers_service_description, "")
        self.assertEqual(service_2.pending_trainers_service_description, "")
        self.assertEqual(service_1.trainers_service_description, "Pomoc při osobním tréninku.")
        self.assertEqual(service_2.trainers_service_description, "Pomoc při online tréninku.")

    def test_unauthorized_access(self):
        self.client.logout()
        response = self.client.get(self.edit_profile_url)
        self.assertRedirects(response, f"{reverse('login')}?next={self.edit_profile_url}")








