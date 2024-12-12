from django.contrib import admin

from accounts.models import UserProfile, Address

admin.site.register(UserProfile)
admin.site.register(Address)

