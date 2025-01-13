from django.contrib.auth.models import Group
from accounts.models import UserProfile, TrainersServices
from django.db.models import Q
from products.models import Category



def navbar_products_context(request):
    """
    Vrací kategorie pro položku 'Produkty' v menu,
    které obsahují produkty typu 'merchantdise'.
    """
    products_categories = Category.objects.filter(
        category_parent=None
    ).filter(
        Q(categories__product_type='merchantdise') | Q(subcategories__categories__product_type='merchantdise')
    ).prefetch_related('subcategories').distinct()

    return {
        'products_categories': products_categories
    }


def navbar_services_context(request):
    """
    Vrací kategorie pro položku 'Služby' v menu,
    které obsahují produkty typu 'service'.
    """
    services_categories = Category.objects.filter(
        category_parent=None
    ).filter(
        Q(subcategories__categories__product_type='service')
    ).prefetch_related('subcategories').distinct()

    return {
        'services_categories': services_categories
    }


def navbar_trainers_context(request):
    # Získání skupiny trenérů
    trainer_group = Group.objects.filter(name='trainer').first()
    if trainer_group:
        # Načtení schválených trenérů (s alespoň jednou schválenou službou)
        approved_trainers = UserProfile.objects.filter(
            groups=trainer_group,
            services__is_approved=True
        ).distinct()
    else:
        approved_trainers = []  # Pokud skupina neexistuje, seznam bude prázdný
    return {
        'approved_trainers': approved_trainers,
    }