from django.contrib import admin

from products.models import Category, Producer, Product

admin.site.register(Category)
admin.site.register(Producer)
admin.site.register(Product)
