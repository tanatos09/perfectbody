from products.models import Category

def navbar_context(request):
    all_main_categories = Category.objects.filter(category_parent=None).prefetch_related('subcategories').distinct()
    return {
        'all_main_categories': all_main_categories
    }


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