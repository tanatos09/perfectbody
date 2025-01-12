from products.models import Category

def navbar_context(request):
    all_main_categories = Category.objects.filter(category_parent=None).prefetch_related('subcategories').distinct()
    return {
        'all_main_categories': all_main_categories
    }
