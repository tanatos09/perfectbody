from django.contrib import admin

from accounts.models import UserProfile, Address, TrainersServices

admin.site.register(UserProfile)
admin.site.register(Address)
admin.site.register(TrainersServices)
