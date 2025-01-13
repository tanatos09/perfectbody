from itertools import groupby
from operator import attrgetter

from django.db.models import Q
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.models import Group
from products.models import Category, Producer, Product
from accounts.models import UserProfile, TrainersServices


def products(request, pk=None):
    # Getting parameters from URL.
    sort_by = request.GET.get('sort_by', 'name')
    gender_filter = request.GET.get('gender', None)
    page_number = request.GET.get('page', 1)

    # Input validation.
    valid_sort_by = ['name', 'price_asc', 'price_desc']
    if sort_by not in valid_sort_by:
        sort_by = 'name'
    valid_gender_filter = ['ladies', 'gentlemans', None]
    if gender_filter not in valid_gender_filter:
        gender_filter = None

    if pk is None:
        # Main categories with merchantdise product type products filter.
        main_categories = Category.objects.filter(
            category_parent=None
        ).filter(
            Q(categories__product_type='merchantdise') | Q(subcategories__categories__product_type='merchantdise')
        ).distinct()

        context = {
            'main_categories': main_categories,
            'category': None,
            'subcategories': None,
            'products': None,
            'sort_by': sort_by,
            'gender_filter': gender_filter,
            'gender_availability': None,    # not applicable for main categories
        }

    else:
        # Getting current category by primary key or return 404.
        category = get_object_or_404(Category, pk=pk)

        # Subcategories with merchantdise product type products filter.
        subcategories = category.subcategories.filter(
            Q(categories__product_type='merchantdise') | Q(subcategories__categories__product_type='merchantdise')
        ).distinct()

        # Filtering products by category.
        products_list = Product.objects.filter(
            category=category,
            product_type='merchantdise'
        ).select_related('category')

        # Checking the availability of filtering by gender.
        gender_availability = {
            'ladies': products_list.filter(product_name__icontains='dámské').exists(),
            'gentlemans': products_list.filter(product_name__icontains='pánské').exists(),
        }

        # Dynamic filtering by gender for products from the sportswear main category.
        if gender_filter == 'ladies':
            products_list = products_list.filter(product_name__icontains='dámské')
        elif gender_filter == 'gentlemans':
            products_list = products_list.filter(product_name__icontains='pánské')

        # Products sorting.
        if sort_by == 'price_asc':
            products_list = products_list.order_by('price')
        elif sort_by == 'price_desc':
            products_list = products_list.order_by('-price')
        else:
            products_list = products_list.order_by('product_name')

        # Pagination.
        paginator = Paginator(products_list, 10)    # 10 products per 1 page
        page_obj = paginator.get_page(page_number)

        context = {
            'main_categories': None,
            'category': category,
            'subcategories': subcategories,
            'products': page_obj,
            'sort_by': sort_by,
            'gender_filter': gender_filter,
            'gender_availability': gender_availability,
        }

    return render(request, 'products.html', context)


def product(request, pk):
    if Product.objects.filter(id=pk):
        product_detail = Product.objects.get(id=pk)
        context = {'product': product_detail}
        return render(request, "product.html", context)
    return products(request)


def producer(request, pk):
    producer_detail = get_object_or_404(Producer, id=pk)

    # Seřazení produktů podle kategorie a následně podle názvu
    products = Product.objects.filter(producer=producer_detail).select_related('category').order_by('category__category_name', 'product_name')

    # Skupinové seskupení produktů podle kategorií
    grouped_products = {}
    for category, items in groupby(products, key=attrgetter('category')):
        grouped_products[category] = list(items)

    # Získání všech výrobců pro seznam a odstranění mezer z názvů
    all_producers = Producer.objects.all().order_by('producer_name')
    for producer in all_producers:
        producer.producer_name = producer.producer_name.strip()

    context = {
        'producer': producer_detail,
        'grouped_products': grouped_products,
        'all_producers': all_producers,  # Přidání seznamu všech výrobců
    }
    return render(request, 'producer.html', context)


def services(request, pk=None):
    # Getting parameters from URL.
    sort_by = request.GET.get('sort_by', 'name')
    page_number = request.GET.get('page', 1)

    # Input validation.
    valid_sort_by = ['name', 'price_asc', 'price_desc']
    if sort_by not in valid_sort_by:
        sort_by = 'name'

    if pk is None:
        # Main categories with service product type filter.
        main_categories = Category.objects.filter(
            category_parent=None
        ).filter(
            Q(categories__product_type='service') | Q(subcategories__categories__product_type='service')
        ).distinct()

        context = {
            'main_categories': main_categories,
            'category': None,
            'subcategories': None,
            'services': None,
            'sort_by': sort_by,
        }
    else:
        # Getting current category by primary key or return 404.
        category = get_object_or_404(Category, pk=pk)

        # Subcategories with service product type filter.
        subcategories = category.subcategories.filter(
            Q(categories__product_type='service') | Q(subcategories__categories__product_type='service')
        ).distinct()

        # Filtering services by category.
        services_list = Product.objects.filter(
            category=category,
            product_type='service'
        ).select_related('category')

        # Services sorting.
        if sort_by == 'price_asc':
            services_list = services_list.order_by('price')
        elif sort_by == 'price_desc':
            services_list = services_list.order_by('-price')
        else:
            services_list = services_list.order_by('product_name')

        # Pagination.
        paginator = Paginator(services_list, 10)    # 10 services per 1 page
        page_obj = paginator.get_page(page_number)

        # Creating a map of approved trainers services for quick lookup.
        approved_trainers_map = {
            service_id: True
            for service_id in TrainersServices.objects.filter(
                service__in=page_obj, is_approved=True
            ).values_list('service_id', flat=True)
        }

        # Assign the has_approved_trainers flag to each service.
        for service in page_obj:
            service.has_approved_trainers = approved_trainers_map.get(service.id, False)

        context = {
            'main_categories': None,
            'category': category,
            'subcategories': subcategories,
            'services': page_obj,
            'sort_by': sort_by,
        }

    return render(request, 'services.html', context)


def service(request, pk):
    # Find the service by primary key or return 404.
    service_detail = get_object_or_404(Product, id=pk)
    # Getting approved trainers for that service.
    approved_trainers_services = TrainersServices.objects.filter(service=service_detail,
                                                                 is_approved=True).select_related('trainer')
    approved_trainers = [ts.trainer for ts in approved_trainers_services]
    context = {'service': service_detail, 'approved_trainers': approved_trainers}
    return render(request, "service.html", context)


def trainers(request):
    trainer_group = Group.objects.filter(name='trainer').first()
    if trainer_group:
        # Checking whether the user from trainer group has at least one approved service.
        approved_trainers = UserProfile.objects.filter(groups=trainer_group, services__is_approved=True).distinct()
    else:
        approved_trainers = []  # If the group does not exist, the list will be empty.
    return render(request, 'trainers.html', {'approved_trainers': approved_trainers})


def trainer(request, pk):
    # Find the trainer by primary key or return 404.
    trainer_detail = get_object_or_404(UserProfile, id=pk)
    # Get approved trainer services.
    approved_services = TrainersServices.objects.filter(trainer=trainer_detail, is_approved=True).select_related(
        'service')
    # Forward approved services only.
    context = {'trainer': trainer_detail, 'approved_services': approved_services}
    return render(request, "trainer.html", context)
