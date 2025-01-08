from django.forms import ModelForm, Textarea

from accounts.models import UserProfile
from products.models import Product, Category, Producer


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

    def save(self, commit=True):
        instance = super().save(commit=False)
        # Automaticky nastavíme product_type na 'merchantdise'
        instance.product_type = 'merchantdise'
        if commit:
            instance.save()
        return instance

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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = Category.objects.filter(
            categories__product_type='service'
        ).distinct()

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.product_type = 'service'
        instance.producer = None
        instance.stock_availability = 0
        if commit:
            instance.save()
        return instance

class TrainerForm(ModelForm):
    class Meta:
        model = UserProfile
        fields = [
            'first_name',
            'last_name',
            'email',
            'phone',
            'profile_picture',
            'trainer_short_description',
            'trainer_long_description',
            'date_of_birth',
        ]
        labels = {
            'first_name': 'Jméno',
            'last_name': 'Příjmení',
            'email': 'E-mail',
            'phone': 'Telefon',
            'profile_picture': 'Profilový obrázek',
            'trainer_short_description': 'Krátký popis trenéra',
            'trainer_long_description': 'Dlouhý popis trenéra',
            'date_of_birth': 'Datum narození',
        }
        widgets = {
            'trainer_long_description': Textarea(attrs={'rows': 5}),
            'trainer_short_description': Textarea(attrs={'rows': 2}),
        }

class ProducerForm(ModelForm):
    class Meta:
        model = Producer
        fields = ['producer_name', 'producer_description', 'producer_view']
        labels = {
            'producer_name': 'Název výrobce',
            'producer_description': 'Popis výrobce',
            'producer_view': 'Logo výrobce (URL)',
        }

class UserForm(ModelForm):
    class Meta:
        model = UserProfile
        fields = ['first_name', 'last_name', 'email', 'phone', 'date_of_birth', 'trainer_short_description', 'trainer_long_description', 'is_staff']
        labels = {
            'first_name': 'Jméno',
            'last_name': 'Příjmení',
            'email': 'Email',
            'phone': 'Telefon',
            'date_of_birth': 'Datum narození',
            'trainer_short_description': 'Krátký popis trenéra',
            'trainer_long_description': 'Dlouhý popis trenéra',
            'is_staff': 'Je admin',
        }
