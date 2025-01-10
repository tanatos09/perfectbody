from django.test import TestCase
from django.urls import reverse
from orders.models import Order, OrderProduct
from products.models import Product, Category, Producer
from accounts.models import UserProfile, Address


class OrderTests(TestCase):
    def setUp(self):
        self.guest_order_url = reverse('start_order')
        self.valid_data = {
            'shipping-first_name': 'Jan',
            'shipping-last_name': 'Novák',
            'shipping-street': 'Hlavní',
            'shipping-street_number': '123',
            'shipping-city': 'Praha',
            'shipping-postal_code': '11000',
            'shipping-country': 'Česká republika',
            'guest_email': 'jan.novak@example.com',
        }
        self.category = Category.objects.create(
            category_name="Testovací kategorie",
            category_description="Popis kategorie"
        )
        self.producer = Producer.objects.create(
            producer_name="Testovací výrobce",
            producer_description="Popis výrobce"
        )
        self.product = Product.objects.create(
            product_type="merchantdise",
            product_name="Testovací produkt",
            product_short_description="Krátký popis produktu",
            product_long_description="Dlouhý popis produktu",
            price=100.0,
            category=self.category,
            producer=self.producer,
            stock_availability=10
        )
        session = self.client.session
        session['cart'] = {
            str(self.product.id): {
                'product_name': self.product.product_name,
                'quantity': 1,
                'price': self.product.price
            }
        }
        session.save()

    def test_order_summary(self):
        product = Product.objects.create(
            product_type="merchantdise",
            product_name="Testovací produkt",
            product_short_description="Krátký popis produktu",
            product_long_description="Dlouhý popis produktu",
            price=100.0,
            category=self.category,
            producer=self.producer,
            stock_availability=10
        )
        user = UserProfile.objects.create_user(
            username="testuser",
            password="testpassword"
        )
        self.client.login(username="testuser", password="testpassword")

        session = self.client.session
        session['cart'] = {
            str(product.id): {
                'product_name': product.product_name,
                'quantity': 2,
                'price': product.price
            }
        }
        session.save()

        self.client.post(reverse('start_order'), {
            'shipping-first_name': "Jan",
            'shipping-last_name': "Novák",
            'shipping-street': "Hlavní",
            'shipping-street_number': "123",
            'shipping-city': "Praha",
            'shipping-postal_code': "11000",
            'shipping-country': "Česká republika",
            'shipping-email': "jan.novak@example.com",
        })

        response = self.client.get(reverse('order_summary'))
        self.assertContains(response, "Testovací produkt")
        self.assertRegex(response.content.decode('utf-8'), r"200[.,]0 Kč")

    def test_start_order_missing_required_fields(self):

        invalid_data = self.valid_data.copy()
        del invalid_data['shipping-last_name']  # Odebrání povinného pole
        response = self.client.post(self.guest_order_url, data=invalid_data)

        self.assertIn(response.status_code, [200, 302])
        if response.status_code == 302:
            self.assertRedirects(response, self.guest_order_url)
        else:
            self.assertContains(response, "Vyplňte všechna povinná pole správně.")

    def test_start_order_shipping_as_billing(self):
        session = self.client.session
        session['cart'] = {
            '1': {'product_name': "Testovací produkt", 'quantity': 2, 'price': 100}
        }
        session.save()

        response = self.client.post(reverse('start_order'), {
            'shipping-first_name': "Jan",
            'shipping-last_name': "Novák",
            'shipping-street': "Hlavní",
            'shipping-street_number': "123",
            'shipping-city': "Praha",
            'shipping-postal_code': "11000",
            'shipping-country': "Česká republika",
            'shipping-email': "jan.novak@example.com",
            'guest_email': "jan.novak@example.com",
        })

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('order_summary'))

    def test_confirm_order_creates_order(self):
        product = Product.objects.create(
            product_type="merchantdise",
            product_name="Testovací produkt",
            product_short_description="Krátký popis produktu",
            product_long_description="Dlouhý popis produktu",
            price=100.0,
            category=self.category,
            producer=self.producer,
            stock_availability=10
        )
        user = UserProfile.objects.create_user(
            username="testuser",
            password="testpassword"
        )
        self.client.login(username="testuser", password="testpassword")

        session = self.client.session
        session['cart_order'] = {
            'cart': {
                str(product.id): {
                    'product_name': product.product_name,
                    'quantity': 2,
                    'price': product.price
                }
            },
            'shipping_address_id': Address.objects.create(
                first_name="Jan",
                last_name="Novák",
                street="Hlavní",
                street_number="123",
                city="Praha",
                postal_code="11000",
                country="Česká republika",
                email="jan.novak@example.com",
            ).id,
            'billing_address_id': Address.objects.create(
                first_name="Jan",
                last_name="Novák",
                street="Hlavní",
                street_number="123",
                city="Praha",
                postal_code="11000",
                country="Česká republika",
                email="jan.novak@example.com",
            ).id,
        }
        session.save()

        response = self.client.get(reverse('confirm_order'))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Order.objects.filter(customer=user).exists())
        self.assertEqual(Order.objects.first().items.count(), 1)

    def test_cancel_pending_order(self):
        user = UserProfile.objects.create_user(
            username="testuser",
            password="testpassword"
        )
        self.client.login(username="testuser", password="testpassword")
        order = Order.objects.create(
            customer=user,
            order_state="PENDING",
            total_price=200.0,
            billing_address=Address.objects.create(
                first_name="Jan",
                last_name="Novák",
                street="Hlavní",
                street_number="123",
                city="Praha",
                postal_code="11000",
                country="Česká republika",
                email="jan.novak@example.com",
            ),
            shipping_address=Address.objects.create(
                first_name="Jan",
                last_name="Novák",
                street="Hlavní",
                street_number="123",
                city="Praha",
                postal_code="11000",
                country="Česká republika",
                email="jan.novak@example.com",
            ),
        )

        response = self.client.get(reverse('cancel_order', args=[order.id]))
        self.assertEqual(response.status_code, 302)
        order.refresh_from_db()
        self.assertEqual(order.order_state, "CANCELLED")

    def test_my_orders_view(self):
        user = UserProfile.objects.create_user(
            username="testuser",
            password="testpassword"
        )
        self.client.login(username="testuser", password="testpassword")
        Order.objects.create(
            customer=user,
            order_state="PENDING",
            total_price=200.0,
            billing_address=Address.objects.create(
                first_name="Jan",
                last_name="Novák",
                street="Hlavní",
                street_number="123",
                city="Praha",
                postal_code="11000",
                country="Česká republika",
                email="jan.novak@example.com",
            ),
            shipping_address=Address.objects.create(
                first_name="Jan",
                last_name="Novák",
                street="Hlavní",
                street_number="123",
                city="Praha",
                postal_code="11000",
                country="Česká republika",
                email="jan.novak@example.com",
            ),
        )

        response = self.client.get(reverse('my_orders'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Objednávka #00000001")

    def test_guest_order(self):

        session = self.client.session
        session['cart'] = {
            str(self.product.id): {
                'product_name': self.product.product_name,
                'quantity': 1,
                'price': self.product.price,
            }
        }
        session.save()

        valid_data = self.valid_data.copy()
        valid_data['shipping-email'] = self.valid_data['guest_email']

        response = self.client.post(self.guest_order_url, data=valid_data)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('order_summary'))

    def test_guest_order_missing_required_fields(self):

        invalid_data = self.valid_data.copy()
        del invalid_data['shipping-first_name']
        response = self.client.post(self.guest_order_url, data=invalid_data)

        self.assertIn(response.status_code, [200, 302])
        if response.status_code == 302:
            self.assertRedirects(response, self.guest_order_url)
        else:
            self.assertContains(response, "Vyplňte všechna povinná pole správně.")

    def test_empty_cart_redirects_to_cart_page(self):

        session = self.client.session
        session['cart'] = {}
        session.save()

        response = self.client.get(reverse('start_order'))

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('cart'))

        messages = list(response.wsgi_request._messages)
        self.assertTrue(any("Váš košík je prázdný." in str(message) for message in messages))










