from django.forms import ModelForm, Form, EmailField, BooleanField, HiddenInput

from accounts.models import Address

class GuestOrderForm(Form):
    guest_email = EmailField(label="E-mail", required=True, error_messages={
        'invalid': "Zadejte platnou e-mailovou adresu.",
        'required': "E-mail je povinný.",
    })



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
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].widget = HiddenInput()


