import logging

from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.forms import ModelForm, CharField, Form, PasswordInput
from django import forms
from accounts.models import UserProfile

logger = logging.getLogger(__name__)

class RegistrationForm(ModelForm):
    password_confirm = CharField(widget=PasswordInput, max_length=128, label='Potvrzení hesla')

    class Meta:
        model = UserProfile
        fields = ['first_name', 'last_name', 'email', 'phone', 'username', 'password']
        widgets = {
            'password': forms.PasswordInput(attrs={'placeholder': 'Zadejte heslo'}),
            'first_name': forms.TextInput(attrs={'placeholder': 'Jméno'}),
            'last_name': forms.TextInput(attrs={'placeholder': 'Příjmení'}),
            'email': forms.EmailInput(attrs={'placeholder': 'E-mail'}),
            'phone': forms.TextInput(attrs={'placeholder': 'Telefon'}),
            'username': forms.TextInput(attrs={'placeholder': 'Uživatelské jméno'}),
        }

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if UserProfile.objects.filter(username=username).exists():
            raise ValidationError('Toto uživatelské jméno již existuje')
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if UserProfile.objects.filter(email=email).exists():
            raise ValidationError('Tento e-mail již existuje.')
        return email

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone and not phone.isdigit():
            raise  ValidationError('Telefoní číslo může obsahovat pouze číslice.')
        return phone

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')

        # Validace hesla pomocí vestavěných validátorů
        if password:
            validate_password(password)

        if password != password_confirm:
            raise ValidationError('Hesla se neshodují.')

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False) # zabrani ulozeni
        user.role = 'CUSTOMER' # nastavi zakaznika jako vychozi hodnotu
        user.account_type = 'REGISTRED' # nastavi zakaznikovi ze je registrovany
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
            logger.info(f"Uživatel {user.username} byl úspěšně registrován.")


class LoginForm(Form):
    username = CharField(max_length=50, label='Uživatelské jméno') # pole pro prihlasovaci jmeno uzivatele
    password = CharField(
        max_length=128,
        widget=PasswordInput,
        label='Heslo'
    ) # pole pro skryte heslo
