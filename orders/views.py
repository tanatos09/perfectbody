from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404

from orders.forms import GuestOrderForm
from orders.models import Order, OrderProduct

from django.forms import modelform_factory
from django.shortcuts import redirect, render
from django.contrib import messages
from accounts.models import Address

def start_order(request):
    cart = request.session.get('cart', {})
    if not cart:
        messages.error(request, 'Váš vozík je prázdný')
        return redirect('view_cart')

    AddressForm = modelform_factory(Address, fields=['first_name', 'last_name', 'street', 'street_number', 'city', 'postal_code', 'country', 'email'])

    if request.method == 'POST':
        different_billing = 'different_billing' in request.POST

        shipping_address_form = AddressForm(request.POST, prefix='shipping')

        billing_address_form = AddressForm(request.POST, prefix='billing') if different_billing else shipping_address_form

        if shipping_address_form.is_valid() and (not different_billing or billing_address_form.is_valid()):
            shipping_address = shipping_address_form.save(commit=False)
            shipping_address.user = request.user if request.user.is_authenticated else None
            shipping_address.save()

            if different_billing:
                billing_address = billing_address_form.save(commit=False)
                billing_address.user = request.user if request.user.is_authenticated else None
                billing_address.save()
            else:
                billing_address = shipping_address

            request.session['cart_order'] = {
                'shipping_address_id': shipping_address.id,
                'billing_address_id': billing_address.id,
                'cart': cart,
            }
            messages.success(request, 'Adresa byla úspěšně uložena. Pokračujte k souhrnu objednávky.')
            return redirect('order_summary')

        messages.error(request, 'Prosím, opravte chyby ve formulářích.')
    else:
        if request.user.is_authenticated:
            primary_address = request.user.addresses.order_by('-id').first()
            initial_shipping = {
                'first_name': primary_address.first_name if primary_address else request.user.first_name,
                'last_name': primary_address.last_name if primary_address else request.user.last_name,
                'street': primary_address.street if primary_address else '',
                'street_number': primary_address.street_number if primary_address else '',
                'city': primary_address.city if primary_address else '',
                'postal_code': primary_address.postal_code if primary_address else '',
                'country': primary_address.country if primary_address else 'Česká republika',
                'email': primary_address.email if primary_address else request.user.email,
            }
            shipping_address_form = AddressForm(initial=initial_shipping, prefix='shipping')

            billing_address_form = AddressForm(initial=initial_shipping, prefix='billing')
        else:
            shipping_address_form = AddressForm(prefix='shipping')
            billing_address_form = AddressForm(prefix='billing')

    return render(request, 'start_order.html', {
        'shipping_address_form': shipping_address_form,
        'billing_address_form': billing_address_form,
        'guest_form': None if request.user.is_authenticated else GuestOrderForm(),
    })


def order_summary(request):
    cart_order = request.session.get('cart_order', {})
    if not cart_order:
        messages.error(request, 'Objednávka nemůže být provedena, protože není připravena')
        return redirect('view_cart')

    shipping_address = Address.objects.get(id=cart_order['shipping_address_id'])
    billing_address = Address.objects.get(id=cart_order['billing_address_id'])
    cart = cart_order['cart']
    guest_email = cart_order.get('guest_email', None)
    total_price = sum(item['quantity'] * item['price'] for item in cart.values())

    if request.method == 'POST':
        return redirect('confirm_order')

    return render(request, 'order_summary.html', {
        'shipping_address': shipping_address,
        'billing_address': billing_address,
        'cart': cart,
        'total_price': total_price,
        'guest_email': guest_email
    })


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

@login_required
def my_orders(request):
    orders = Order.objects.filter(customer=request.user).order_by('-order_creation_datetime')
    return render(request, 'my_orders.html', {'orders': orders})

@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, customer=request.user)
    return render(request, 'order_detail.html', {'order': order})


