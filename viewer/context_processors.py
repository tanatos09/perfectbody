# viewer/context_processors.py
from products.models import Category
def navbar_context(request):
    main_categories = Category.objects.filter(category_parent=None).prefetch_related('subcategories').distinct()
    return {
        'main_categories': main_categories
    }