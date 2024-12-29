from django.contrib.auth.models import AbstractUser
from django.db.models import Model, DateTimeField, CharField, URLField, ForeignKey, SET_NULL, BooleanField, \
    IntegerField, EmailField, TextField, DateField

from perfectbody.settings import AUTH_USER_MODEL


class UserProfile(AbstractUser):
    PREFERRED_CHANNEL = [('PHONE', 'Telefón'), ('EMAIL', 'Email'), ('POST', 'Pošta')]
    ACCOUNT_TYPES = [('registered', 'Registrovaný uživatel'), ('guest', 'Neregistrovaný uživatel')]

    avatar = URLField(blank=True, null=True)  # url avataru
    phone = CharField(max_length=15, blank=True, null=True)  # telefon
    preferred_channel = CharField(max_length=10, choices=PREFERRED_CHANNEL, default='EMAIL')  # prefer. kom. kanal, vyber z PREFERRED_CHANNEL
    trainer_short_description = TextField(blank=True, null=True)
    trainer_long_description = TextField(blank=True, null=True)
    date_of_birth = DateField(blank=True, null=True)
    created_at = DateTimeField(auto_now_add=True) # datum vytvoreni uctu
    account_type = CharField(max_length=15, choices=ACCOUNT_TYPES, default='registered')

    def __str__(self):
        return f'{self.username} - {self.first_name} {self.last_name}'

    def __repr__(self):
        return f'username={self.username},last_login={self.last_login}, is_superuser={self.is_superuser}, is_staff={self.is_staff}'

    def full_name(self):
        return f'{self.first_name} {self.last_name}'


class Address(Model):

    user = ForeignKey(AUTH_USER_MODEL, on_delete=SET_NULL, null=True, blank=True, related_name='addresses')
    first_name = CharField(max_length=255)
    last_name = CharField(max_length=255)
    street = CharField(max_length=255)
    street_number = CharField(max_length=255)
    city = CharField(max_length=255)
    postal_code = CharField(max_length=255)
    country = CharField(max_length=255, default='Česká republika')
    email = EmailField()

    def __str__(self):
        return f'{self.first_name} {self.last_name}, {self.street}, {self.street_number}, {self.city}, {self.country}, {self.postal_code}, {self.email}'

    def __repr__(self):
        return f'user_id={self.user_id}, first_name={self.first_name}, last_name={self.last_name}, street={self.street}, city={self.city}, postal_code={self.postal_code}, country={self.country}, email={self.email}'

