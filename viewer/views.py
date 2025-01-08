import json
import logging
from itertools import groupby
from operator import attrgetter

import requests
import unicodedata
from django.db.models import Q
from django.urls import reverse
from unidecode import unidecode
from django.contrib.auth.models import Group
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.models import Group
from products.models import Category, Producer, Product
from accounts.models import UserProfile, TrainersServices, Address
from datetime import datetime, timedelta
from django.http import JsonResponse


def clean_city_name(city):
    return ''.join(c for c in city if not c.isdigit()).strip()

def translate_weather_description(description):
    translations = {
        "Sunny": "Slunečno",
        "Cloudy": "Zataženo",
        "Partly cloudy": "Částečně zataženo",
        "Mist": "Mlha",
        "Rain": "Déšť",
        "Snow": "Sníh",
        "Thunderstorm": "Bouřka",
        "Fog": "Mlha",
        "Clear": "Jasno",
        "Overcast": "Převážně zataženo",
        "Light rain": "Slabý déšť",
        "Heavy rain": "Silný déšť",
        "Light snow": "Slabé sněžení",
        "Heavy snow": "Silné sněžení",
        "Showers": "Přeháňky",
        "Drizzle": "Mrholení",
        "Light drizzle": "Slabé mrholení",
        "Heavy drizzle": "Silné mrholení",
        "Hail": "Kroupy",
        "Sleet": "Déšť se sněhem",
        "Blizzard": "Vánice",
        "Freezing rain": "Mrznoucí déšť",
        "Windy": "Větrno",
        "Breezy": "Mírný vítr",
        "Gale": "Bouřlivý vítr",
        "Hurricane": "Hurikán",
        "Tornado": "Tornádo",
    }
    return translations.get(description, description)

def get_weather(city):
    try:
        url = f"https://wttr.in/{city}?format=j1"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            current_condition = data['current_condition'][0]
            return {
                'city': city,
                'temperature': current_condition['temp_C'],
                'description': translate_weather_description(current_condition['weatherDesc'][0]['value']),
                'humidity': current_condition['humidity'],
            }
    except Exception as e:
        print(f"Chyba při získávání počasí: {e}")
    return None

def home(request):
    name_day = get_name_day()

    default_cities = ['Brno', 'Praha', 'Ostrava']
    weather_data = []

    if request.user.is_authenticated:
        address = Address.objects.filter(user=request.user).order_by('-id').first()
        if address:
            user_city = clean_city_name(address.city)
            weather = get_weather(user_city)
            if weather:
                weather_data.append(weather)

    if not weather_data:
        for city in default_cities:
            weather = get_weather(city)
            if weather:
                weather_data.append(weather)

    return render(request, 'home.html', {'name_day': name_day, 'weather_data': weather_data})

def get_name_day():
    try:
        response = requests.get('https://nameday.abalin.net/api/V1/today?country=cz')
        if response.status_code == 200:
            data = response.json()
            if 'nameday' in data and 'cz' in data['nameday']:
                return data['nameday']['cz']
            else:
                return "Není dostupné"
        else:
            return "API nedostupné"
    except Exception as e:
        print(f"Chyba při získávání jmenin: {e}")
        return "Chyba"

logger = logging.getLogger(__name__)
def products(request, pk=None):
    sort_by = request.GET.get('sort_by', 'name')

    if pk is None:
        # Zobrazí hlavní kategorie, které obsahují produkty nebo podkategorie s produkty typu 'merchantdise'
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
        }

    else:
        # Zobrazení konkrétní kategorie
        category = get_object_or_404(Category, pk=pk)

        subcategories = category.subcategories.filter(
            Q(categories__product_type='merchantdise') | Q(subcategories__categories__product_type='merchantdise')
        ).distinct()

        # Produkty v aktuální kategorii
        if sort_by == 'price_asc':
            products = Product.objects.filter(category=category, product_type='merchantdise').order_by('price')
        elif sort_by == 'price_desc':
            products = Product.objects.filter(category=category, product_type='merchantdise').order_by('-price')
        else:
            products = Product.objects.filter(category=category, product_type='merchantdise').order_by('product_name')

        context = {
            'main_categories': None,
            'category': category,
            'subcategories': subcategories,
            'products': products,
            'sort_by': sort_by,
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
    products = Product.objects.filter(producer=producer_detail).select_related('category').order_by('category')

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
    sort_by = request.GET.get('sort_by', 'name')

    if pk is None:
        # Získání hlavních kategorií, které mají přes podkategorie služby typu 'service'
        main_categories = Category.objects.filter(
            category_parent=None,  # Hlavní kategorie
            subcategories__categories__product_type='service'  # Služby v podkategoriích typu 'service'
        ).distinct()

        context = {
            'main_categories': main_categories,
            'category': None,
            'subcategories': None,
            'services': None,
            'sort_by': sort_by,
        }
    else:
        # Načtení aktuální kategorie
        category = get_object_or_404(Category, pk=pk)

        # Načtení podkategorií a služeb
        subcategories = category.subcategories.all()

        # Řazení produktů na základě parametru sort_by
        if sort_by == 'price_asc':
            services = Product.objects.filter(category=category, product_type='service').order_by('price')
        elif sort_by == 'price_desc':
            services = Product.objects.filter(category=category, product_type='service').order_by('-price')
        else:
            services = Product.objects.filter(category=category, product_type='service').order_by('product_name')

        # Kontrola schválených trenérů pro každou službu
        for service in services:
            service.has_approved_trainers = TrainersServices.objects.filter(service=service, is_approved=True).exists()

        context = {
            'main_categories': None,
            'category': category,
            'subcategories': subcategories,
            'services': services,
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

def add_to_cart(request, product_id):
    # Načtení košíku ze session
    cart = request.session.get('cart', {})
    product_id_str = str(product_id)
    product = get_object_or_404(Product, id=product_id)

    if product.product_type == 'service':
        # Kontrola, zda má služba schválené trenéry
        has_approved_trainers = TrainersServices.objects.filter(service=product, is_approved=True).exists()
        if not has_approved_trainers:
            messages.error(request, "Pro tuto službu nejsou k dispozici schválení trenéři.")
            return redirect('service', pk=product_id)
    else:
        # Kontrola skladové dostupnosti pro zboží
        if product.available_stock() <= 0:
            messages.error(request, "Produkt není skladem.")
            return redirect('product', pk=product_id)

    # Přidání produktu nebo služby do košíku
    if product_id_str in cart:
        if product.product_type == 'service' or cart[product_id_str]['quantity'] < product.available_stock():
            cart[product_id_str]['quantity'] += 1
        else:
            messages.error(request, "Nelze přidat více, než je dostupné množství.")
            return redirect('product', pk=product_id)
    else:
        cart[product_id_str] = {
            'name': product.product_name,
            'price': float(product.price),
            'quantity': 1,
        }

    # Uložení košíku do session
    request.session['cart'] = cart

    messages.success(request, f"{product.product_name} byl přidán do košíku.")
    return redirect('cart')

def view_cart(request):
    # Získání košíku ze session
    cart = request.session.get('cart', {})

    # Výpočet celkové ceny a jednotlivých částek
    for product_id, item in cart.items():
        item['total'] = item['quantity'] * item['price']
    total = sum(item['quantity'] * item['price'] for item in cart.values())

    # Zobrazení stránky košíku
    return render(request, 'cart.html', {"cart": cart, "total": total})

def remove_from_cart(request, product_id):
    # Získání košíku ze session
    cart = request.session.get('cart', {})
    product_id_str = str(product_id)

    if product_id_str in cart:
        # Odebrání položky z košíku
        del cart[product_id_str]
        request.session['cart'] = cart

        messages.success(request, "Produkt byl odstraněn z košíku.")
    else:
        messages.error(request, "Produkt nebyl nalezen v košíku.")

    return redirect('cart')

def update_cart(request, product_id):
    # Získání košíku ze session
    cart = request.session.get('cart', {})
    product_id_str = str(product_id)

    if product_id_str in cart:
        try:
            # Získání nového množství z POST dat
            new_quantity = int(request.POST.get('quantity', 1))
            if new_quantity > 0:
                # Aktualizace množství v košíku
                cart[product_id_str]['quantity'] = new_quantity
            else:
                # Odstranění položky, pokud je nové množství 0 nebo méně
                del cart[product_id_str]
        except ValueError:
            # Ošetření chybného vstupu
            messages.error(request, "Neplatná hodnota množství.")
            return redirect('cart')

    # Aktualizace session
    request.session['cart'] = cart
    messages.success(request, "Košík byl úspěšně aktualizován.")
    return redirect('cart')

def update_cart_ajax(request, product_id):
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        cart = request.session.get('cart', {})
        product_id_str = str(product_id)

        # Získání produktu a jeho skladové zásoby
        product = get_object_or_404(Product, id=product_id)

        if product_id_str in cart:
            try:
                data = json.loads(request.body)
                new_quantity = int(data.get('quantity', 1))

                if new_quantity > 0:
                    # Kontrola skladové dostupnosti
                    if new_quantity > product.available_stock():
                        return JsonResponse({
                            'success': False,
                            'error': f'Na skladě je k dispozici pouze {product.available_stock()} kusů.'
                        })

                    # Aktualizace množství v košíku
                    cart[product_id_str]['quantity'] = new_quantity
                    request.session['cart'] = cart

                    # Přepočet celkové ceny
                    total = sum(item['quantity'] * item['price'] for item in cart.values())
                    item_total = cart[product_id_str]['quantity'] * cart[product_id_str]['price']

                    return JsonResponse({
                        'success': True,
                        'item_total': f"{item_total:.2f} Kč",
                        'cart_total': f"{total:.2f} Kč"
                    })
                else:
                    # Odstranění položky z košíku, pokud je nové množství 0 nebo méně
                    del cart[product_id_str]
                    request.session['cart'] = cart

                    total = sum(item['quantity'] * item['price'] for item in cart.values())
                    return JsonResponse({'success': True, 'cart_total': f"{total:.2f} Kč"})

            except (ValueError, KeyError):
                return JsonResponse({'success': False, 'error': 'Neplatná hodnota množství.'})
        else:
            return JsonResponse({'success': False, 'error': 'Produkt nebyl nalezen v košíku.'})

    return JsonResponse({'success': False, 'error': 'Neplatný požadavek.'})

def user_profile_view(request, username):
    user = get_object_or_404(UserProfile, username=username)
    is_trainer = user.groups.filter(name='trainer').exists()

    if request.user.is_authenticated and request.user == user:
        return redirect('profile')

    if is_trainer:
        approved_services = TrainersServices.objects.filter(trainer=user, is_approved=True).select_related('service')
        return render(request, 'trainer.html', {
            'trainer': user,
            'approved_services': approved_services,
        })

    return render(request, 'user_profile.html', {
        'user': user,
        'is_trainer': is_trainer,
    })


def get_name_day():
    try:
        response = requests.get('https://nameday.abalin.net/api/V1/today?country=cz')
        if response.status_code == 200:
            data = response.json()
            if 'nameday' in data and 'cz' in data['nameday']:
                return data['nameday']['cz']
            else:
                return "Není dostupné"
        else:
            return "API nedostupné"
    except Exception as e:
        return f"Chyba: {e}"


def normalize_for_search(text):
    return ''.join(
        c for c in unicodedata.normalize('NFD', text.lower())
        if unicodedata.category(c) != 'Mn'
    )

def search(request):
    query = request.GET.get('q', '').strip()
    if not query:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True, 'results': []})
        return render(request, 'search_results.html', {
            'query': query,
            'products': [],
            'services': [],
            'trainers': [],
        })

    normalized_query = normalize_for_search(query)

    # Vyhledávání produktů
    products = [
        {
            'id': product.id,
            'name': product.product_name,
            'description': product.product_short_description,
            'url': reverse('product', args=[product.id])
        }
        for product in Product.objects.filter(product_type='merchantdise')
        if normalized_query in normalize_for_search(product.product_name)
           or normalized_query in normalize_for_search(product.product_short_description or "")
    ]

    # Vyhledávání služeb
    services = [
        {
            'id': service.id,
            'name': service.product_name,
            'description': service.product_short_description,
            'url': reverse('service', args=[service.id])
        }
        for service in Product.objects.filter(product_type='service')
        if normalized_query in normalize_for_search(service.product_name)
           or normalized_query in normalize_for_search(service.product_short_description or "")
    ]

    # Vyhledávání trenérů se schválenými službami
    trainers = UserProfile.objects.filter(
        groups__name='trainer',
        services__is_approved=True
    ).distinct()

    filtered_trainers = [
        {
            'username': trainer.username,
            'name': f"{trainer.first_name} {trainer.last_name}",
            'description': trainer.trainer_short_description,
            'url': reverse('user_profile', args=[trainer.username])
        }
        for trainer in trainers
        if (
            normalized_query in normalize_for_search(trainer.username)
            or normalized_query in normalize_for_search(trainer.first_name)
            or normalized_query in normalize_for_search(trainer.last_name)
            or normalized_query in normalize_for_search(trainer.trainer_short_description or "")
        )
    ]

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'results': {
                'products': products,
                'services': services,
                'trainers': filtered_trainers,
            }
        })

    return render(request, 'search_results.html', {
        'query': query,
        'products': products,
        'services': services,
        'trainers': filtered_trainers,
    })
