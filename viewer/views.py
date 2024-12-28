import requests
from unidecode import unidecode
from django.contrib.auth.models import Group
from django.shortcuts import render, get_object_or_404, redirect

from accounts.models import UserProfile, Address
from products.models import Product


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
    }
    return translations.get(description, description)

def get_weather(city):
    url = f"https://wttr.in/{city}?format=j1"
    try:
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
        else:
            print(f"Chyba API Wttr.in: {response.status_code}")
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


def products(request):
    products = Product.objects.filter(product_type='merchantdise')
    print(products)
    return render(request, 'products.html', {'products': products})

def product(request, pk):
    if Product.objects.filter(id=pk):
        product_detail = Product.objects.get(id=pk)
        context = {'product': product_detail}
        return render(request, "product.html", context)
    return products(request)

def services(request):
    services = Product.objects.filter(product_type='service')
    return render(request, 'services.html', {"services": services})

def service(request, pk):
    if Product.objects.filter(id=pk):
        service_detail = Product.objects.get(id=pk)
        context = {'service': service_detail}
        return render(request, "service.html", context)
    return services(request)

def trainers(request):
    return render(request, 'trainers.html')

def add_to_cart(request, product_id):
    cart = request.session.get('cart', {})
    product_id_str = str(product_id)
    product = get_object_or_404(Product, id=product_id)
    if product_id_str in cart:
        cart[product_id_str]['quantity'] += 1
    else:
        cart[product_id_str] = {
            'name': product.product_name,
            'price': float(product.price),
            'quantity': 1,
        }

    request.session['cart'] = cart
    return redirect('cart')

def view_cart(request):
    cart = request.session.get('cart', {})
    total = sum(item['quantity'] * item['price'] for item in cart.values())
    return render(request, 'cart.html', {"cart": cart, "total": total})

def remove_from_cart(request, product_id):
    cart = request.session.get('cart', {})
    product_id_str = str(product_id)

    if product_id_str in cart:
        del cart[product_id_str]

    request.session['cart'] = cart
    return redirect('cart')

def update_cart(request, product_id):
    cart = request.session.get('cart', {})
    product_id_str = str(product_id)

    if product_id_str in cart:
        new_quantity = int(request.POST.get('quantity', 1))
        if new_quantity > 0:
            cart[product_id_str]['quantity'] = new_quantity
        else:
            del cart[product_id_str]

    request.session['cart'] = cart
    return redirect('cart')

def user_profile_view(request, username):
    user = get_object_or_404(UserProfile, username=username)
    is_trainer = user.groups.filter(name='trainer').exists()
    if request.user.is_authenticated and request.user == user:
        return redirect('profile')
    return render(request, 'user_profile.html', {'user': user, 'is_trainer': is_trainer})

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
    return unidecode(text).lower()

#FIXME - pri vyhledani sluzby se nalezne sluzba ale zaroven i produkt - opravit, zkus vyhledat HIIT a pochopis
def search(request):
    query = request.GET.get('q', '').strip()
    normalized_query = normalize_for_search(query)
    products = []
    services = []
    trainers = []

    if query:
        all_products = Product.objects.all()
        products = [
            product for product in all_products
            if normalized_query in normalize_for_search(product.product_name)
            or normalized_query in normalize_for_search(product.product_description or "")
        ]

        all_services = Product.objects.filter(product_type='service')
        services = [
            service for service in all_services
            if normalized_query in normalize_for_search(service.product_name)
            or normalized_query in normalize_for_search(service.product_description or "")
        ]

        try:
            trainers_group = Group.objects.get(name='trainer')
            all_trainers = UserProfile.objects.filter(groups__in=[trainers_group])
            trainers = [
                trainer for trainer in all_trainers
                if normalized_query in normalize_for_search(trainer.first_name)
                or normalized_query in normalize_for_search(trainer.last_name)
            ]
        except Group.DoesNotExist:
            trainers = []

    return render(request, 'search_results.html', {
        'query': query,
        'products': products,
        'services': services,
        'trainers': trainers,
    })
