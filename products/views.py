from itertools import groupby
from operator import attrgetter

from django import template
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import connection
from django.db.models import Q, Avg

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import Group
from django.urls import reverse

from products.models import Category, Producer, Product, TrainerReview, ProductReview
from accounts.models import UserProfile, TrainersServices

import czech_sort


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

        # Czech sort for main categories
        main_categories = sorted(
            main_categories,
            key=lambda category: czech_sort.key(category.category_name)
        )

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

        # Czech sort for subcategories
        subcategories = sorted(
            subcategories,
            key=lambda subcategory: czech_sort.key(subcategory.category_name)
        )

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
            products_list = list(products_list)  # Convert queryset to list for Czech sorting
            products_list = sorted(
                products_list,
                key=lambda product: czech_sort.key(product.product_name)
            )

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
    product_detail = get_object_or_404(Product, pk=pk)

    stock = product_detail.available_stock()

    print(f"DEBUG: Product ID {product_detail.id}, Stock Availability: {stock}")

    reviews = ProductReview.objects.filter(product=product_detail)
    average_rating = reviews.aggregate(Avg('rating'))['rating__avg']
    rounded_rating = round(average_rating * 2) / 2 if average_rating else 0

    star_states = []
    for i in range(1, 6):
        if i <= rounded_rating:
            star_states.append("filled")
        elif i - 0.5 == rounded_rating:
            star_states.append("half-filled")
        else:
            star_states.append("empty")

    paginator = Paginator(reviews, 5)
    page_number = request.GET.get('page')
    page_reviews = paginator.get_page(page_number)

    if stock > 0:
        stock_message = f"Skladem: {stock} kusů"
        can_add_to_cart = True
    else:
        stock_message = "Produkt není skladem."
        can_add_to_cart = False

    context = {
        'product': product_detail,
        'available_stock': stock,
        'stock_message': stock_message,
        'can_add_to_cart': can_add_to_cart,
        'average_rating': rounded_rating,
        'star_states': star_states,
        'page_reviews': page_reviews,
    }
    return render(request, "product.html", context)

def producer(request, pk):
    producer_detail = get_object_or_404(Producer, id=pk)

    # Seřazení produktů podle kategorie a následně podle názvu produktu
    products = Product.objects.filter(producer=producer_detail).select_related('category')

    # Czech sort for categories and products
    products = sorted(
        products,
        key=lambda product: (
            czech_sort.key(product.category.category_name) if product.category else "",
            czech_sort.key(product.product_name)
        )
    )

    # Skupinové seskupení produktů podle kategorií
    grouped_products = {}
    for category, items in groupby(products, key=attrgetter('category')):
        grouped_products[category] = list(items)

    # Získání všech výrobců pro seznam a odstranění mezer z názvů
    all_producers = Producer.objects.all()
    all_producers = sorted(
        all_producers,
        key=lambda producer: czech_sort.key(producer.producer_name.strip())
    )

    context = {
        'producer': producer_detail,
        'grouped_products': grouped_products,
        'all_producers': all_producers,
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
    service_detail = get_object_or_404(Product, pk=pk, product_type='service')

    approved_trainers_services = TrainersServices.objects.filter(
        service=service_detail,
        is_approved=True
    ).select_related('trainer')

    reviews = ProductReview.objects.filter(product=service_detail)
    average_rating = reviews.aggregate(Avg('rating'))['rating__avg']
    rounded_rating = round(average_rating * 2) / 2 if average_rating else 0

    star_states = []
    for i in range(1, 6):
        if i <= rounded_rating:
            star_states.append("filled")
        elif i - 0.5 == rounded_rating:
            star_states.append("half-filled")
        else:
            star_states.append("empty")

    paginator = Paginator(reviews, 5)
    page_number = request.GET.get('page')
    page_reviews = paginator.get_page(page_number)

    context = {
        'service': service_detail,
        'approved_trainers_services': approved_trainers_services,
        'average_rating': rounded_rating,
        'star_states': star_states,
        'page_reviews': page_reviews,
        'user': request.user,
    }
    return render(request, "service.html", context)

def trainers(request):
    # Získání skupiny trenérů
    trainer_group = Group.objects.filter(name='trainer').first()
    if trainer_group:
        # Načtení schválených trenérů (s alespoň jednou schválenou službou)
        approved_trainers = UserProfile.objects.filter(
            groups=trainer_group,
            services__is_approved=True
        ).distinct()

        # Řazení trenérů podle české abecedy pomocí czech_sort
        approved_trainers = sorted(
            approved_trainers,
            key=lambda trainer: czech_sort.key(trainer.full_name())
        )
    else:
        approved_trainers = []  # Pokud skupina neexistuje, seznam bude prázdný

    return render(request, 'trainers.html', {'approved_trainers': approved_trainers})

def trainer(request, pk):
    trainer_detail = get_object_or_404(UserProfile, id=pk)

    approved_services = TrainersServices.objects.filter(
        trainer=trainer_detail, is_approved=True
    ).select_related('service')

    reviews = TrainerReview.objects.filter(trainer=trainer_detail)
    average_rating = reviews.aggregate(Avg('rating'))['rating__avg']
    rounded_rating = round(average_rating * 2) / 2 if average_rating else 0

    star_states = []
    for i in range(1, 6):
        if i <= rounded_rating:
            star_states.append("filled")
        elif i - 0.5 == rounded_rating:
            star_states.append("half-filled")
        else:
            star_states.append("empty")

    paginator = Paginator(reviews, 5)
    page_number = request.GET.get('page')
    page_reviews = paginator.get_page(page_number)

    context = {
        'trainer': trainer_detail,
        'approved_services': approved_services,
        'average_rating': rounded_rating,
        'star_states': star_states,
        'page_reviews': page_reviews,
    }
    return render(request, "trainer.html", context)

@login_required
def add_trainer_review(request, pk):
    trainer = get_object_or_404(UserProfile, pk=pk, groups__name='trainer')
    if request.method == "POST":
        rating = request.POST.get('rating')
        comment = request.POST.get('comment')

        review, created = TrainerReview.objects.update_or_create(
            trainer=trainer,
            reviewer=request.user,
            defaults={
                'rating': rating,
                'comment': comment,
            }
        )

        if created:
            messages.success(request, "Hodnocení bylo přidáno.")
        else:
            messages.info(request, "Vaše hodnocení bylo aktualizováno.")

        return redirect(reverse('trainer', args=[pk]))
@login_required
def add_product_review(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == "POST":
        rating = request.POST.get('rating')
        comment = request.POST.get('comment')

        review, created = ProductReview.objects.update_or_create(
            product=product,
            reviewer=request.user,
            defaults={
                'rating': rating,
                'comment': comment,
            }
        )

        if created:
            messages.success(request, "Hodnocení bylo přidáno.")
        else:
            messages.info(request, "Vaše hodnocení bylo aktualizováno.")

        return redirect(reverse('product', args=[pk]))

@login_required
def add_service_review(request, pk):
    service = get_object_or_404(Product, pk=pk, product_type='service')
    if request.method == "POST":
        rating = request.POST.get('rating')
        comment = request.POST.get('comment')
        trainer_id = request.POST.get('trainer')

        trainer = get_object_or_404(UserProfile, pk=trainer_id, groups__name='trainer')

        if not TrainersServices.objects.filter(service=service, trainer=trainer, is_approved=True).exists():
            messages.error(request, "Vybraný trenér tuto službu neposkytuje.")
            return redirect(reverse('service', args=[pk]))

        review, created = ProductReview.objects.update_or_create(
            product=service,
            reviewer=request.user,
            comment__contains=f"(Tato služba byla poskytnuta trenérem: {trainer.full_name()})",
            defaults={
                'rating': rating,
                'comment': f"{comment} (Tato služba byla poskytnuta trenérem: {trainer.full_name()})",
            }
        )

        if created:
            messages.success(request, "Hodnocení bylo přidáno.")
        else:
            messages.info(request, "Vaše hodnocení bylo aktualizováno.")

        return redirect(reverse('service', args=[pk]))

def calculate_average_rating(queryset):
    average_rating = queryset.aggregate(Avg('rating'))['rating__avg']
    return round(average_rating, 1) if average_rating else 0
