from django.forms import ModelForm, Form, EmailField

from accounts.models import Address

class GuestOrderForm(Form):
    email = EmailField(label='Email', required=True)


class OrderAddressForm(ModelForm):
    class Meta:
        model = Address
        fields = ['first_name', 'last_name', 'street', 'street_number', 'city', 'postal_code', 'country', 'email']
        labels = {
            'first_name': 'Jméno',
            'last_name': 'Příjmení',
            'street': 'Ulice',
            'street_number': 'Číslo domu',
            'city': 'Město',
            'postal_code': 'PSČ',
            'country': 'Země',
            'email': 'E-mail',
        }

