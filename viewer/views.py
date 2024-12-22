from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from products.models import Product
from datetime import datetime, timedelta


def home(request):
    return render(request, 'home.html')

def products(request):
    products = Product.objects.filter(product_type='merchantdise').order_by('category__category_name', 'product_name')
    return render(request, 'products.html', {'products': products})

def product(request, pk):
    if Product.objects.filter(id=pk):
        product_detail = Product.objects.get(id=pk)
        context = {'product': product_detail}
        return render(request, "product.html", context)
    return products(request)

def services(request):
    services = Product.objects.filter(product_type='service').order_by('category__category_name', 'product_name')
    return render(request, 'services.html', {"services": services})

def service(request, pk):
    if Product.objects.filter(id=pk):
        service_detail = Product.objects.get(id=pk)
        context = {'service': service_detail}
        return render(request, "service.html", context)
    return services(request)

def trainers(request):
    return render(request, 'trainers.html')

def validate_last_activity(last_activity):
    try:
        return datetime.fromisoformat(last_activity)
    except (ValueError, TypeError):
        return None

def add_to_cart(request, product_id):
    cart = request.session.get('cart', {})
    last_activity = request.session.get('cart_last_activity')

    # Validation of last activity.
    last_activity_time = validate_last_activity(last_activity)
    if last_activity_time and datetime.now() - last_activity_time > timedelta(minutes=15):
        # Clearing the cart and releasing the reservation.
        for product_id_str, item in cart.items():
            product = get_object_or_404(Product, id=int(product_id_str))
            product.reserved_stock -= item['quantity']
            product.save()
        request.session['cart'] = {}
        request.session['cart_last_activity'] = None
        messages.info(request, "Váš košík byl z důvodu neaktivity vyprázdněn.")
        return redirect('cart')

    product_id_str = str(product_id)
    product = get_object_or_404(Product, id=product_id)

    if product.available_stock() <= 0:
        messages.error(request, "Produkt není skladem.")
        return redirect('product', product_id=product_id)

    if product_id_str in cart:
        if cart[product_id_str]['quantity'] >= product.available_stock():
            messages.error(request, "Nelze přidat více, než je dostupné množství.")
            return redirect('product', product_id=product_id)
        cart[product_id_str]['quantity'] += 1
    else:
        cart[product_id_str] = {
            'name': product.product_name,
            'price': float(product.price),
            'quantity': 1,
        }

    reserved_quantity = cart[product_id_str]['quantity']
    if reserved_quantity <= product.available_stock():
        product.reserved_stock += 1
        product.save()
    else:
        messages.error(request, "Nelze přidat více produktů do košíku, než je dostupné množství.")
        return redirect('product', product_id=product_id)

    request.session['cart_last_activity'] = datetime.now().isoformat()
    request.session['cart'] = cart
    messages.success(request, "Produkt byl přidán do košíku.")
    return redirect('cart')

def view_cart(request):
    cart = request.session.get('cart', {})
    last_activity = request.session.get('cart_last_activity')

    last_activity_time = validate_last_activity(last_activity)
    if last_activity_time and datetime.now() - last_activity_time > timedelta(minutes=15):
        # Clearing the cart and releasing the reservation.
        for product_id_str, item in cart.items():
            product = get_object_or_404(Product, id=int(product_id_str))
            product.reserved_stock -= item['quantity']
            product.save()
        request.session['cart'] = {}
        request.session['cart_last_activity'] = None
        messages.info(request, "Váš košík byl z důvodu neaktivity vyprázdněn.")
        return redirect('cart')

    total = sum(item['quantity'] * item['price'] for item in cart.values())
    return render(request, 'cart.html', {"cart": cart, "total": total})

def remove_from_cart(request, product_id):
    cart = request.session.get('cart', {})
    product_id_str = str(product_id)

    if product_id_str in cart:
        product = get_object_or_404(Product, id=product_id)
        quantity = cart[product_id_str]['quantity']

        if product.reserved_stock >= quantity:
            product.reserved_stock -= quantity
            product.save()
        else:
            messages.error(request, "Nelze odstranit více položek, než je rezervováno.")
            return redirect('cart')

        del cart[product_id_str]
        request.session['cart'] = cart

        # Timestamp update
        request.session['cart_last_activity'] = datetime.now().isoformat()

        messages.success(request, f"Produkt {product.product_name} byl odstraněn z košíku.")
    else:
        messages.error(request, "Produkt nebyl nalezen v košíku.")

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

def complete_order(request):
    cart = request.session.get('cart', {})
    if not cart:
        messages.error(request, "Váš košík je prázdný.")
        return redirect('cart')

    for product_id_str, item in cart.items():
        product = get_object_or_404(Product, id=int(product_id_str))
        quantity = item['quantity']

        if product.reserved_stock >= quantity:
            product.stock_availability -= quantity
            product.reserved_stock -= quantity
            product.save()
        else:
            messages.error(request, f"Nedostatek zboží: {product.product_name}.")
            return redirect('cart')

    # Clearing the cart after completing the order.
    request.session['cart'] = {}
    messages.success(request, "Objednávka byla úspěšně dokončena.")
    return redirect('products')
