import logging

from django.contrib.auth import user_logged_in
from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db import transaction
from django.forms import ModelForm, CharField, Form, PasswordInput, BooleanField, TextInput, EmailInput

from accounts.models import UserProfile, Address

logger = logging.getLogger(__name__)

class RegistrationForm(ModelForm):
    password_confirm = CharField(widget=PasswordInput, max_length=128, label='Potvrzení hesla')
    add_address = BooleanField(required=False, label='Chci zadat adresu pro budoucí nákup')
    street = CharField(max_length=255, required=False, label='Ulice')
    street_number = CharField(max_length=255, required=False, label='Číslo ulice')
    city = CharField(max_length=255, required=False, label='Město')
    postal_code = CharField(max_length=255, required=False, label='PSČ')
    country = CharField(max_length=255, required=False, label='Země', initial='Česká republika')

    class Meta:
        model = UserProfile
        fields = ['first_name', 'last_name', 'email', 'phone', 'username', 'password']
        widgets = {
            'password': PasswordInput(attrs={'placeholder': 'Zadejte heslo'}),
            'first_name': TextInput(attrs={'placeholder': 'Jméno'}),
            'last_name': TextInput(attrs={'placeholder': 'Příjmení'}),
            'email': EmailInput(attrs={'placeholder': 'E-mail'}),
            'phone': TextInput(attrs={'placeholder': 'Telefon'}),
            'username': TextInput(attrs={'placeholder': 'Uživatelské jméno'}),
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

    def clean_postal_code(self):
        postal_code = self.cleaned_data.get('postal_code')
        if postal_code and not postal_code.isdigit():
            raise ValidationError('PSČ musi obsahovat pouze číslice')
        return postal_code

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')

        try:
            if password:
                validate_password(password)
        except ValidationError as e:
            self.add_error('password', e)

        if password != password_confirm:
            self.add_error('password_confirm', 'Hesla se neshodují.')

        if cleaned_data.get('add_address'):
            for field, label in [
                ('street', 'Ulice'),
                ('street_number', 'Číslo ulice'),
                ('city', 'Město'),
                ('postal_code', 'PSČ'),
                ('country', 'Země')
            ]:
                if not cleaned_data.get(field):
                    self.add_error(field, f'Pole {label} je povinné, pokud zadáváte adresu')
        return cleaned_data

    def save(self, commit=True):
        with transaction.atomic():
            user = super().save(commit=False) # zabrani ulozeni
            user.account_type = 'registered' # nastavi zakaznikovi ze je registrovany
            user.set_password(self.cleaned_data['password'])
            if commit:
                user.save()
                logger.info(f"Uživatel {user.username} byl úspěšně registrován.")
                if self.cleaned_data.get('add_address'):
                    Address.objects.create(
                        user=user,
                        first_name=user.first_name,
                        last_name=user.last_name,
                        street=self.cleaned_data['street'],
                        street_number=self.cleaned_data['street_number'],
                        city=self.cleaned_data['city'],
                        postal_code=self.cleaned_data['postal_code'],
                        country=self.cleaned_data['country'],
                        email=self.cleaned_data['email'],
                    )
        return user


class LoginForm(Form):
    username = CharField(max_length=50, label='Uživatelské jméno') # pole pro prihlasovaci jmeno uzivatele
    password = CharField(
        max_length=128,
        widget=PasswordInput,
        label='Heslo'
    ) # pole pro skryte heslo

class UserEditForm(UserChangeForm):
    password = None

    class Meta:
        model = UserProfile
        fields = ['username', 'first_name', 'last_name', 'email', 'phone', 'avatar', 'preferred_channel']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if UserProfile.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise ValidationError('Tento email již existuje.')
        return email

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone and not phone.isdigit():
            raise ValidationError('Telefoní číslo může obsahovat pouze číslice.')
        return phone




