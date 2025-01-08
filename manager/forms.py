from django.forms import ModelForm
from products.models import Product, Category

class ProductForm(ModelForm):
    class Meta:
        model = Product
        fields = ['product_name', 'product_short_description', 'product_long_description', 'price', 'category', 'producer', 'stock_availability']
        labels = {
            'product_name': 'Název produktu',
            'product_short_description': 'Krátký popis produktu',
            'product_long_description': 'Dlouhý popis produktu',
            'price': 'Cena',
            'category': 'Kategorie',
            'producer': 'Výrobce',
            'stock_availability': 'Dostupnost skladem (počet kusů)',
        }
        help_texts = {
            'price': 'Zadejte cenu produktu v korunách.',
            'stock_availability': 'Počet kusů skladem (pouze pro zboží).',
        }

class CategoryForm(ModelForm):
    class Meta:
        model = Category
        fields = ['category_name', 'category_description', 'category_view', 'category_parent']
        labels = {
            'category_name': 'Název kategorie',
            'category_description': 'Popis kategorie',
            'category_view': 'Obrázek kategorie (Image URL)',
            'category_parent': 'Nadřazená kategorie',
        }
        help_texts = {
            'category_name': 'Zadejte název kategorie.',
            'category_description': 'Popište, o jakou kategorii se jedná.',
            'category_parent': 'Pokud jde o podkategorii, vyberte nadřazenou kategorii.',
        }

class ServiceForm(ModelForm):
    class Meta:
        model = Product
        fields = ['product_name', 'product_short_description', 'product_long_description', 'price', 'category']
        labels = {
            'product_name': 'Název služby',
            'product_short_description': 'Krátký popis služby',
            'product_long_description': 'Dlouhý popis služby',
            'price': 'Cena služby',
            'category': 'Kategorie služby',
        }
        help_texts = {
            'price': 'Zadejte cenu služby v korunách.',
        }

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.product_type = 'service'
        if commit:
            instance.save()
        return instance
