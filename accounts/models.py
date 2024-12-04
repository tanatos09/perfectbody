from django.contrib.auth.models import AbstractUser
from django.db.models import Model, DateTimeField, CharField, EmailField, URLField


class UserProfile(AbstractUser):
    PREFERRED_CHANNEL = [('PHONE', 'Telefón'), ('EMAIL', 'Email'), ('POST', 'Pošta')]

    avatar = URLField(blank=True, null=True)  # url avataru
    phone = CharField(max_length=15, blank=True, null=True)  # telefon
    preferred_channel = CharField(max_length=10, choices=PREFERRED_CHANNEL, default='EMAIL')  # prefer. kom. kanal, vyber z PREFERRED_CHANNEL
    created_at = DateTimeField(auto_now_add=True) # datum vytvoreni uctu
