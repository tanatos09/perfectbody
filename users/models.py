from django.db.models import Model, DateTimeField, CharField, EmailField, URLField


class User(Model):
    ACCOUNT_TYPE = [('REGISTERED', 'Registrovaný'), ('UNREGISTERED', 'Neregistrovaný')]
    ROLE = [('ADMIN', 'Administrator'), ('MANAGER', 'Manager'), ('COACH', 'Trenér'), ('CUSTOMER', 'Zákazník')]
    PREFERRED_CHANNEL = [('PHONE', 'Telefón'), ('EMAIL', 'Email'), ('POST', 'Pošta')]

    account_type = CharField(max_length=15, choices=ACCOUNT_TYPE)  # typy uctu, vyber z ACCOUNT_TYPE
    role = CharField(max_length=15, choices=ROLE, default='CUSTOMER')  # role uzivatele, vyber z ROLE
    login = CharField(max_length=50, unique=True)  # prihlasovaci jmeno
    password = CharField(max_length=128)  # heslo
    avatar = URLField(blank=True, null=True)  # url avataru
    first_name = CharField(max_length=50)  # jmeno
    last_name = CharField(max_length=50)  # prijmeni
    phone = CharField(max_length=15, blank=True, null=True)  # telefon
    email = EmailField(unique=True)  # email
    preferred_channel = CharField(max_length=10, choices=PREFERRED_CHANNEL)  # prefer. kom. kanal, vyber z PREFERRED_CHANNEL
    created_at = DateTimeField(auto_now_add=True) # datum vytvoreni uctu
