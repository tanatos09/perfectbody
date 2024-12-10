from django.shortcuts import render, get_object_or_404, redirect

from products.models import Product


def home(request):
    return render(request, 'home.html')

def products(request):
    products = Product.objects.filter(product_type='merchantdise')
    print(products)
    return render(request, 'products.html', {'products': products})

def services(request):
    services = Product.objects.filter(product_type='service')
    return render(request, 'services.html', {"services": services})

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


