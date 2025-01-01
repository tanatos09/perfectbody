from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.models import Group
from products.models import Product, TrainersServices, Category
from accounts.models import UserProfile
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
    for service in services:
        service.has_approved_trainers = TrainersServices.objects.filter(service=service, is_approved=True).exists()
    return render(request, 'services.html', {"services": services})

def service(request, pk):
    # Find the service by primary key or return 404.
    service_detail = get_object_or_404(Product, id=pk)

    # Getting approved trainers for that service.
    approved_trainers_services = TrainersServices.objects.filter(service=service_detail, is_approved=True).select_related('trainer')
    approved_trainers = [ts.trainer for ts in approved_trainers_services]
    context = {'service': service_detail, 'approved_trainers': approved_trainers}
    return render(request, "service.html", context)

def trainers(request):
    trainer_group = Group.objects.filter(name='trainer').first()
    if trainer_group:
        # Checking whether the user from trainer group has at least one approved service.
        approved_trainers = UserProfile.objects.filter(groups=trainer_group, services__is_approved=True).distinct()
    else:
        approved_trainers = [] # If the group does not exist, the list will be empty.
    return render(request, 'trainers.html', {'approved_trainers': approved_trainers})

def trainer(request, pk):
    # Find the trainer by primary key or return 404.
    trainer_detail = get_object_or_404(UserProfile, id=pk)
    # Get approved trainer services.
    approved_services = TrainersServices.objects.filter(trainer=trainer_detail, is_approved=True).select_related('service')
    # Forward approved services only.
    context = {'trainer': trainer_detail, 'approved_services': approved_services}
    return render(request, "trainer.html", context)

def category(request, category_id):
    category_detail = get_object_or_404(Category, id=category_id)
    products = Product.objects.filter(category=category_detail)
    context = {'category': category_detail, 'products': products}
    return render(request, 'category.html', context)

def validate_last_activity(last_activity):
    try:
        return datetime.fromisoformat(last_activity)
    except (ValueError, TypeError):
        return None

def check_cart_inactivity(request):
    """
    Check the timestamp of the last activity in the cart.
    If the time limit is exceeded, the cart is emptied and the reservation is released.
    """
    cart = request.session.get('cart', {})
    last_activity = request.session.get('cart_last_activity')

    last_activity_time = validate_last_activity(last_activity)
    if last_activity_time and datetime.now() - last_activity_time > timedelta(minutes=15):
        # Emptying the cart and releasing the reservation.
        for product_id_str, item in cart.items():
            product = get_object_or_404(Product, id=int(product_id_str))
            product.reserved_stock -= item['quantity']
            product.save()
        request.session['cart'] = {}
        request.session['cart_last_activity'] = None
        messages.info(request, "Váš košík byl z důvodu neaktivity vyprázdněn.")
        return True  # Indicates that the cart has been emptied.
    return False  # Indicates that the cart is still active.

def add_to_cart(request, product_id):
    # Cart inactivity checking.
    if check_cart_inactivity(request):
        # If inactivity is detected, the cart will be emptied.
        return redirect('cart')

    cart = request.session.get('cart', {})
    product_id_str = str(product_id)
    product = get_object_or_404(Product, id=product_id)

    if product.available_stock() <= 0:
        messages.error(request, "Produkt není skladem.")
        # Redirect to the product detail page.
        if product.product_type == 'service':
            return redirect('service', pk=product_id)
        return redirect('product', product_id=product_id)

    if product_id_str in cart:
        if cart[product_id_str]['quantity'] >= product.available_stock():
            messages.error(request, "Nelze přidat více, než je dostupné množství.")
            # Redirect to the product detail page.
            if product.product_type == 'service':
                return redirect('service', pk=product_id)
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
        # Redirect to the product detail page.
        if product.product_type == 'service':
            return redirect('service', pk=product_id)
        return redirect('product', product_id=product_id)

    request.session['cart_last_activity'] = datetime.now().isoformat()
    request.session['cart'] = cart
    messages.success(request, f"Produkt {product.product_name} přidán do košíku.")

    # Redirect to cart for all product types.
    return redirect('cart')

def view_cart(request):
    # Cart inactivity checking.
    if check_cart_inactivity(request):
        # If inactivity is detected, the cart will be emptied.
        return redirect('cart')

    cart = request.session.get('cart', {})
    total = sum(item['quantity'] * item['price'] for item in cart.values())
    return render(request, 'cart.html', {"cart": cart, "total": total})

def remove_from_cart(request, product_id):
    # Cart inactivity checking.
    if check_cart_inactivity(request):
        # If inactivity is detected, the cart will be emptied.
        return redirect('cart')

    cart = request.session.get('cart', {})
    product_id_str = str(product_id)

    if product_id_str in cart:
        product = get_object_or_404(Product, id=product_id)
        removed_quantity = cart[product_id_str]['quantity']

        # Product type checking.
        if product.product_type != 'service': # It is necessary to update the stock availability for products.
            if product.reserved_stock >= removed_quantity:
                product.reserved_stock -= removed_quantity
                product.save()
            else:
                messages.error(request, "Nelze odstranit více položek, než je rezervováno.")
                return redirect('cart')

        # Removing an item from the cart.
        del cart[product_id_str]
        request.session['cart'] = cart
        request.session['cart_last_activity'] = datetime.now().isoformat()

        messages.success(request, f"Produkt {product.product_name} byl odstraněn z košíku.")
    else:
        messages.error(request, "Produkt nebyl nalezen v košíku.")

    return redirect('cart')

def update_cart(request, product_id):
    # Checking cart inactivity.
    if check_cart_inactivity(request):
        # If inactivity is detected, the cart will be emptied.
        return redirect('cart')

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
    # Cart inactivity checking.
    if check_cart_inactivity(request):
        # If inactivity is detected, the cart will be emptied.
        return redirect('cart')

    # Retrieving the cart after checking for inactivity.
    cart = request.session.get('cart', {})
    if not cart:
        messages.error(request, "Váš košík je prázdný.")
        return redirect('cart')

    # Order processing.
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

    # Emptying the cart after completing the order.
    request.session['cart'] = {}
    request.session['cart_last_activity'] = None
    messages.success(request, "Objednávka byla úspěšně dokončena.")
    return redirect('products')
