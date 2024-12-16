from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import redirect, render, get_object_or_404

from accounts.models import Address
from orders.forms import OrderAddressForm, GuestOrderForm
from orders.models import Order, OrderProduct


def start_order(request):
    cart = request.session.get('cart', {})
    if not cart:
        messages.error(request, 'Váš vozík je prázdný')
        return redirect('view_cart')

    if request.method == 'POST':
        if request.user.is_authenticated:
            address_form = OrderAddressForm(request.POST)
            if address_form.is_valid():
                address = address_form.save(commit=False)
                address.user = request.user
                address.save()

                request.session['cart_order'] = {
                    'address_id': address.id,
                    'cart': cart,
                }
                return redirect('order_summary')
        else:
            guest_form = GuestOrderForm(request.POST)
            address_form = OrderAddressForm(request.POST)
            if guest_form.is_valid() and address_form.is_valid():
                guest_email = guest_form.cleaned_data['email']
                address = address_form.save(commit=False)
                address.save()

                request.session['cart_order'] = {
                    'address_id': address.id,
                    'cart': cart,
                    'guest_email': guest_email,
                }
                request.session['guest_email'] = guest_email
                return redirect('order_summary')
    else:
        guest_form = GuestOrderForm() if not request.user.is_authenticated else None
        address_form = OrderAddressForm()

    return render(request, 'start_order.html', {'address_form': address_form, 'guest_form': guest_form})


def order_summary(request):
    cart_order = request.session.get('cart_order', {})
    if not cart_order:
        messages.error(request, 'Objednávka nemůže být provedena, protože není připravena')
        return redirect('view_cart')

    address = Address.objects.get(id=cart_order['address_id'])
    cart = cart_order['cart']
    guest_email = cart_order.get('guest_email', None)
    total_price = sum(item['quantity'] * item['price'] for item in cart.values())

    if request.method == 'POST':
        return redirect('confirm_order')

    return render(request, 'order_summary.html', {'address': address, 'cart': cart, 'total_price': total_price, 'guest_email': guest_email})

def confirm_order(request):
    cart_order = request.session.get('cart_order', {})
    if not cart_order:
        messages.error(request, 'Objednávka nemůže být provedena, protože není připravena')
        return redirect('view_cart')

    address = Address.objects.get(id=cart_order['address_id'])
    cart = cart_order['cart']
    guest_email = cart_order.get('guest_email', None)

    order = Order.objects.create(
        customer=request.user if request.user.is_authenticated else None,
        guest_email=guest_email,
        billing_address=address,
        shipping_address=address,
        total_price=sum(item['quantity'] * item['price'] for item in cart.values())
    )

    for product_id, item in cart.items():
        OrderProduct.objects.create(
            order=order,
            product_id=product_id,
            quantity=item['quantity'],
            price_per_item=item['price'],
        )
    messages.success(request, f'Děkujeme za objednávku #{order.id}')
    return redirect('thank_you', order_id=order.id)

def thank_you(request, order_id):
    if request.user.is_authenticated:
        try:
            order = Order.objects.get(id=order_id, customer=request.user)
        except Order.DoesNotExist:
            return HttpResponse(f"Objednávka s ID {order_id} pro uživatele {request.user} nebyla nalezena.")
    else:
        guest_email = request.session.get('guest_email')
        try:
            order = Order.objects.get(id=order_id, guest_email=guest_email)
        except Order.DoesNotExist:
            return HttpResponse(f"Objednávka s ID {order_id} pro hosta s e-mailem {guest_email} nebyla nalezena.")

    return render(request, 'thank_you.html', {'order': order})

#TODO - neni nikde prirazeno zobrazeni mych objednavek a detail objednavky
def my_orders(request):
    orders = Order.objects.filter(customer=request.user).order_by('-order_creation_datetime')
    return render(request, 'my_orders.html', {'orders': orders})

def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, customer=request.user)
    return render(request, 'order_detail.html', {'order': order})


