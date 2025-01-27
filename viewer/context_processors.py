from django.contrib.auth.models import Group
from accounts.models import UserProfile, TrainersServices
from django.db.models import Q
from products.models import Category

import czech_sort


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

    # Řazení kategorií podle české abecedy
    products_categories = sorted(
        products_categories,
        key=lambda category: czech_sort.key(category.category_name)
    )

    # Řazení podkategorií u každé kategorie
    for category in products_categories:
        subcategories = category.subcategories.all()
        category.sorted_subcategories = sorted(
            subcategories,
            key=lambda subcategory: czech_sort.key(subcategory.category_name)
        )

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
        Q(categories__product_type='service') | Q(subcategories__categories__product_type='service')
    ).prefetch_related('subcategories').distinct()

    # Řazení kategorií podle české abecedy
    services_categories = sorted(
        services_categories,
        key=lambda category: czech_sort.key(category.category_name)
    )

    # Řazení podkategorií u každé kategorie
    for category in services_categories:
        subcategories = category.subcategories.all()
        category.sorted_subcategories = sorted(
            subcategories,
            key=lambda subcategory: czech_sort.key(subcategory.category_name)
        )

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

        # Řazení trenérů podle české abecedy
        approved_trainers = sorted(
            approved_trainers,
            key=lambda trainer: czech_sort.key(trainer.full_name())
        )
    else:
        approved_trainers = []  # Pokud skupina neexistuje, seznam bude prázdný

    return {
        'approved_trainers': approved_trainers,
    }
