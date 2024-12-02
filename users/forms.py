from django.forms import ModelForm, CharField, Form, PasswordInput
from django import forms
from users.models import User


class RegistrationForm(ModelForm):
    class Meta:
        model = User
        fields =  ['first_name', 'last_name', 'email', 'phone', 'login', 'password']
        widgets = {'password': forms.PasswordInput()} #skryje heslo pri zadavani

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
