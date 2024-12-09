from http.client import responses

from django.test import TestCase
from django.urls import reverse
from accounts.models import UserProfile


class RegisterViewTest(TestCase):
    def test_register_user(self):
        """Test uspesne registrace.
        """
        # vytvoreni uzivatele pro vyplneni formulare
        registration_data = {
            'first_name': 'Honza',
            'last_name': 'Novák',
            'email': 'jenda.novak@seznam.cz',
            'phone': '00420777888999',
            'username': 'jendajeborec',
            'password': 'TotoJeSuperHeslo123!',
            'password_confirm': 'TotoJeSuperHeslo123!',
            'add_address': False,
        }

        # simulace pozadavku pro registraci
        response = self.client.post(reverse('register'), data=registration_data)

        # kontrola presmerovani na stranku login
        self.assertRedirects(response, reverse('login'))

        # overovani jestli byl uzivatel v databazi
        self.assertTrue(UserProfile.objects.filter(username='jendajeborec').exists())

        # pristup ke zpravam, kontola ze byla pridana, kontrola obsahu
        messages = list(response.wsgi_request._messages)
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Registrace proběhla úspěšně. Nyní se můžete přihlásit.")

    def test_register_user_invalid_passwords(self):
        """Test selhání registrace při ruznych heslech.
        """
        # vytvoreni uzivatele s rozdilnymi hesly
        invalid_data = {
            'first_name': 'Honza',
            'last_name': 'Novák',
            'email': 'jenda.novak@seznam.cz',
            'phone': '00420777888999',
            'username': 'jendajeborec',
            'password': 'TotoJeSuperHeslo123!',
            'password_confirm': 'TotoJeSpatneHeslo',
            'add_address': False,
        }

        # vytvoreni pozadavku pro registraci
        response = self.client.post(reverse('register'), data=invalid_data)

        # overeni ze byl vracen kod 200 - 'chybova hlaska' uspesna
        self.assertEqual(response.status_code, 200)

        # zobrazeni chybove hlasky
        self.assertContains(response, 'Hesla se neshodují')

        # kontrola ze ucet nebyl vytvoren
        self.assertFalse(UserProfile.objects.filter(username='jendajeborec').exists())

    def test_register_user_duplicate_username(self):
        """Test selhání registrace při duplicitním uživatelském jménu.
        """

        # vytvoreni uuzivatele s duplicitnim uzivatelskym jmenem
        UserProfile.objects.create(username='jendajeborec', email='JenadaNovak@seznam.cz')

        duplicate_user_data = {
            'first_name': 'Honza',
            'last_name': 'Novak',
            'email': 'JendaJinyEmail@seznam.cz',
            'phone': '00420777888999',
            'username': 'jendajeborec',
            'password': 'UltraSuperSilneHeslo123!',
            'password_confirm': 'UltraSuperSilneHeslo123!',
            'add_address': False,
        }

        # pozadavek POST pro registraci
        response = self.client.post(reverse('register'), data=duplicate_user_data)

        # overeni ze byl vracen kod 200 - 'chybova hlaska' uspesna
        self.assertEqual(response.status_code, 200)

        # kontrola chybove hlasky
        self.assertContains(response, 'Toto uživatelské jméno již existuje')

        # kontrola ze nebyl vytvoren novy uzivatel
        self.assertEqual(UserProfile.objects.filter(username='jendajeborec').count(), 1)

    def test_register_user_with_adress(self):
        '''Test uspesne registrace s vyplnenou adresou
        '''
        registration_data = {
        'first_name': 'Pavel',
        'last_name': 'Novotný',
        'email': 'pavel.novotny@seznam.cz',
        'phone': '00420777888988',
        'username': 'pavelnovotny',
        'password': 'SilneHeslo123!',
        'password_confirm': 'SilneHeslo123!',
        'add_address': True,
        'street': 'Hlavní',
        'street_number': '123',
        'city': 'Praha',
        'postal_code': '11000',
        'country': 'Česká republika',
    }

        response = self.client.post(reverse('register'), data=registration_data)
        self.assertRedirects(response, reverse('login'))
        self.assertTrue(UserProfile.objects.filter(username='pavelnovotny').exists())

        user = UserProfile.objects.get(username='pavelnovotny')
        self.assertTrue(user.addresses.exists())
        address = user.addresses.first()
        self.assertTrue(address.street, 'Hlavní')
        self.assertTrue(address.city, 'Praha')
        self.assertTrue(address.postal_code, '11000')

    def test_register_user_with_missing_address_data(self):
        registration_data = {
            'first_name': 'Pavel',
            'last_name': 'Novotný',
            'email': 'pavel.novotny@seznam.cz',
            'phone': '00420777888988',
            'username': 'pavelnovotny',
            'password': 'SilneHeslo123!',
            'password_confirm': 'SilneHeslo123!',
            'add_address': True,
            'street': '',
            'street_number': '',
            'city': '',
            'postal_code': '',
            'country': '',
        }

        response = self.client.post(reverse('register'), data=registration_data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Pole Ulice je povinné, pokud zadáváte adresu')
        self.assertContains(response, 'Pole Číslo ulice je povinné, pokud zadáváte adresu')
        self.assertContains(response, 'Pole Město je povinné, pokud zadáváte adresu')
        self.assertContains(response, 'Pole PSČ je povinné, pokud zadáváte adresu')
        self.assertContains(response, 'Pole Země je povinné, pokud zadáváte adresu')

    def test_register_user_with_missing_postal_code(self):
        registration_data = {
            'first_name': 'Pavel',
            'last_name': 'Novotný',
            'email': 'pavel.novotny@seznam.cz',
            'phone': '00420777888988',
            'username': 'pavelnovotny',
            'password': 'SilneHeslo123!',
            'password_confirm': 'SilneHeslo123!',
            'add_address': True,
            'street': 'Hlavní',
            'street_number': '123',
            'city': 'Praha',
            'postal_code': 'AbC123',
            'country': 'Česká republika',
        }

        response = self.client.post(reverse('register'), data=registration_data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'PSČ musi obsahovat pouze číslice')
        self.assertFalse(UserProfile.objects.filter(username='pavelnovotny').exists())