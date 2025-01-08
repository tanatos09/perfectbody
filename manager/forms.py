from django.db.models import CharField
from django.forms import ModelForm

from products.models import Product, Category
from viewer.views import product


class ProductForm(ModelForm):
    class Meta:
        model = Product
        fields = '__all__'

class CategoryForm(ModelForm):
    class Meta:
        model = Category
        fields = ['category_name', 'category_description', 'category_parent', 'category_view']

class ServiceForm(ModelForm):
    class Meta:
        model = Product
        fields = ['product_name', 'product_short_description', 'product_long_description', 'price', 'category']

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.product_type = 'service'
        if commit:
            instance.save()
        return instance

class ProductForm(ModelForm):
    class Meta:
        model = Product
        fields = ['product_name', 'product_short_description', 'product_long_description', 'price', 'category', 'producer', 'stock_availability']
