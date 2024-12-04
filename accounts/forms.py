from django.core.exceptions import ValidationError
from django.forms import ModelForm, CharField, Form, PasswordInput
from django import forms
from accounts.models import UserProfile


class RegistrationForm(ModelForm):
    password_confirm = CharField(widget=PasswordInput, max_length=128, label='Potvrzení hesla')

    class Meta:
        model = UserProfile
        fields =  ['first_name', 'last_name', 'email', 'phone', 'login', 'password']
        widgets = {'password': forms.PasswordInput()} #skryje heslo pri zadavani

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

            if password != password_confirm:
                raise ValidationError('Hesla se neshodují.')

            return cleaned_data

        def save(self, commit=True):
            user = super().save(commit=False) # zabrani ulozeni
            user.role = 'CUSTOMER' # nastavi zakaznika jako vychozi hodnotu
            user.account_type = 'REGISTRED' # nastavi zakaznikovi ze je registrovany
            if commit:
                user.save()
            return user

class LoginForm(Form):
    username = CharField(max_length=50, label='Uživatelské jméno') # pole pro prihlasovaci jmeno uzivatele
    password = CharField(
        max_length=128,
        widget=PasswordInput,
        label='Heslo'
    ) # pole pro skryte heslo
