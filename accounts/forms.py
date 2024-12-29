import logging

from django.contrib.auth import user_logged_in
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.contrib.auth.models import Group
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db import transaction
from django.forms import ModelForm, CharField, Form, PasswordInput, BooleanField, TextInput, EmailInput, Textarea, \
    ModelMultipleChoiceField, CheckboxSelectMultiple, DateField, DateInput

from accounts.models import UserProfile, Address
from products.models import Product, TrainersServices

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


class TrainerRegistrationForm(RegistrationForm):
    trainer_short_description = CharField(
        max_length=500,
        required=True,
        widget=Textarea(attrs={'placeholder': "Úvodní představení se v seznamu trenérů (maximálně 500 znaků)."}),
        label='Představení trenéra'
    )
    trainer_long_description = CharField(
        widget=Textarea(attrs={'placeholder': "Prozraďte nám podrobnosti o vaší životní cestě a zkušenostech do vašeho medailonku."}),
        required=True,
        label='Detail trenéra'
    )
    services = ModelMultipleChoiceField(
        queryset=Product.objects.filter(product_type='service'),
        widget=CheckboxSelectMultiple,
        label="Vyberte služby, které nabízíte"
    )
    trainers_services_descriptions = CharField(
        widget=Textarea(attrs={'placeholder': "Popište svůj jedinečný přístup ke každé vybrané službě. Uveďte vaše dosavadní zkušenosti s vybranou službou, kurzy a certifikáty."}),
        required=True,
        label="Popis služeb (oddělte jednotlivé popisy pomocí '---')"
    )
    date_of_birth = DateField(
        required=True,
        widget=DateInput(attrs={'type': 'date'}),
        label="Datum narození"
    )
    add_address = BooleanField(required=False, label="Chci zadat adresu")
    street = CharField(max_length=255, required=False, label="Ulice")
    street_number = CharField(max_length=255, required=False, label="Číslo ulice")
    city = CharField(max_length=255, required=False, label="Město")
    postal_code = CharField(max_length=10, required=False, label="PSČ")
    country = CharField(max_length=255, required=False, label="Země", initial="Česká republika")

    def clean(self):
        cleaned_data = super().clean()
        services = cleaned_data.get('services')
        descriptions = cleaned_data.get('trainers_services_descriptions')

        if not services:
            self.add_error('services', 'Musíte vybrat alespoň jednu službu.')

        if services and descriptions:
            descriptions_list = descriptions.split('---')
            if len(descriptions_list) != len(services):
                self.add_error(
                    'trainers_services_descriptions',
                    f'Počet popisů ({len(descriptions_list)}) musí odpovídat počtu vybraných služeb ({len(services)}).'
                )

        if cleaned_data.get('add_address'):
            required_address_fields = [
                ('street', 'Ulice'),
                ('street_number', 'Číslo ulice'),
                ('city', 'Město'),
                ('postal_code', 'PSČ'),
                ('country', 'Země'),
            ]
            for field, label in required_address_fields:
                if not cleaned_data.get(field):
                    self.add_error(field, f'Pole {label} je povinné, pokud zadáváte adresu.')
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.account_type = 'registered'
        user.trainer_short_description = self.cleaned_data.get('trainer_short_description')
        user.trainer_long_description = self.cleaned_data.get('trainer_long_description')

        if commit:
            user.save()
            trainer_group, created = Group.objects.get_or_create(name='trainer')
            user.groups.add(trainer_group)

            # Uložení služeb a jejich popisů
            services = self.cleaned_data.get('services')
            descriptions = self.cleaned_data.get('trainers_services_descriptions').split('---')
            for service, description in zip(services, descriptions):
                TrainersServices.objects.create(
                    trainer=user,
                    service=service,
                    trainers_service_description=description.strip()
                )

            # Uložení adresy
            if self.cleaned_data.get('add_address'):
                Address.objects.create(
                    user=user,
                    first_name=user.first_name,
                    last_name=user.last_name,
                    street=self.cleaned_data.get('street'),
                    street_number=self.cleaned_data.get('street_number'),
                    city=self.cleaned_data.get('city'),
                    postal_code=self.cleaned_data.get('postal_code'),
                    country=self.cleaned_data.get('country'),
                    email=user.email,
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

class PasswordChangeForm(Form):
    old_password = CharField(widget=PasswordInput, required=True, label='Současné heslo')
    new_password = CharField(widget=PasswordInput, required=True, label='Nové heslo')
    confirm_password = CharField(widget=PasswordInput, required=True, label='Potvrzení nového hesla')

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        old_password = cleaned_data.get('old_password')
        new_password = cleaned_data.get('new_password')
        confirm_password = cleaned_data.get('confirm_password')

        if not self.user.check_password(old_password):
            raise ValidationError('Původní heslo není správné')

        if new_password != confirm_password:
            raise ValidationError('Hesla se neshodují!')

        try:
            validate_password(new_password, user=self.user)
        except ValidationError as e:
            self.add_error('new_password', e)

        return cleaned_data

    def save(self):
        new_password = self.cleaned_data.get('new_password')
        self.user.set_password(new_password)
        self.user.save()


