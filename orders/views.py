from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q
from django.forms import modelform_factory

from accounts.models import Address
from orders.models import Order, OrderProduct


def normalize_address_data(address_data):
    return {
        key: value.strip().lower() if isinstance(value, str) else value
        for key, value in address_data.items()
    }


def get_or_create_address(user, **address_data):
    """
    Najde existující adresu konkrétního uživatele nebo vytvoří novou.
    """
    normalized_data = normalize_address_data(address_data)

    address = Address.objects.filter(
        Q(user=user if user.is_authenticated else None) &
        Q(first_name=normalized_data['first_name']) &
        Q(last_name=normalized_data['last_name']) &
        Q(street=normalized_data['street']) &
        Q(street_number=normalized_data['street_number']) &
        Q(city=normalized_data['city']) &
        Q(postal_code=normalized_data['postal_code']) &
        Q(country=normalized_data['country']) &
        Q(email=normalized_data['email'])
    ).first()

    if address:
        return address

    return Address.objects.create(
        user=user if user.is_authenticated else None,
        **address_data
    )



def get_initial_data(user):
    if user.is_authenticated:
        primary_address = user.addresses.order_by('-id').first()
        return {
            'first_name': primary_address.first_name if primary_address else user.first_name,
            'last_name': primary_address.last_name if primary_address else user.last_name,
            'street': primary_address.street if primary_address else '',
            'street_number': primary_address.street_number if primary_address else '',
            'city': primary_address.city if primary_address else '',
            'postal_code': primary_address.postal_code if primary_address else '',
            'country': primary_address.country if primary_address else 'Česká republika',
            'email': primary_address.email if primary_address else user.email,
        }
    return {}


def start_order(request):
    cart = request.session.get('cart', {})
    if not cart:
        messages.error(request, 'Váš vozík je prázdný.')
        return redirect('cart')

    AddressForm = modelform_factory(
        Address,
        fields=['first_name', 'last_name', 'street', 'street_number', 'city', 'postal_code', 'country', 'email']
    )

    guest_email = request.session.get('guest_email', '')

    if request.method == 'POST':
        shipping_address_form = AddressForm(request.POST, prefix='shipping')
        billing_address_form = AddressForm(request.POST, prefix='billing') if 'different_billing' in request.POST else None

        # Získání hostujícího e-mailu z POST dat
        guest_email = request.POST.get('guest_email')

        shipping_valid = shipping_address_form.is_valid()
        billing_valid = billing_address_form.is_valid() if billing_address_form else True

        if not request.user.is_authenticated and not guest_email:
            messages.error(request, 'Hostující e-mail je povinný.')
            return render(request, 'start_order.html', {
                'shipping_address_form': shipping_address_form,
                'billing_address_form': billing_address_form,
                'guest_email': guest_email,
            })

        if shipping_valid and billing_valid:
            # Uložení adresy a e-mailu do session
            shipping_address = shipping_address_form.save(commit=False)
            shipping_address.user = request.user if request.user.is_authenticated else None
            shipping_address.save()

            billing_address = (
                billing_address_form.save(commit=False)
                if billing_address_form else shipping_address
            )
            if billing_address_form:
                billing_address.user = request.user if request.user.is_authenticated else None
                billing_address.save()

            # Uložení dat do session
            request.session['cart_order'] = {
                'shipping_address_id': shipping_address.id,
                'billing_address_id': billing_address.id,
                'cart': cart,
            }
            if not request.user.is_authenticated:
                request.session['guest_email'] = guest_email

            messages.success(request, 'Adresa byla úspěšně uložena.')
            return redirect('order_summary')

        messages.error(request, 'Vyplňte všechna povinná pole správně.')
    else:
        initial_data = {}
        if request.user.is_authenticated:
            initial_data = {
                'first_name': request.user.first_name,
                'last_name': request.user.last_name,
                'email': request.user.email,
            }
        shipping_address_form = AddressForm(initial=initial_data, prefix='shipping')
        billing_address_form = AddressForm(prefix='billing')

    return render(request, 'start_order.html', {
        'shipping_address_form': shipping_address_form,
        'billing_address_form': billing_address_form,
        'guest_email': guest_email,
    })



def order_summary(request):
    cart_order = request.session.get('cart_order', None)
    if not cart_order:
        messages.error(request, 'Objednávka není připravena.')
        return redirect('cart')

    try:
        shipping_address = Address.objects.get(id=cart_order['shipping_address_id'])
        billing_address = Address.objects.get(id=cart_order['billing_address_id'])
    except Address.DoesNotExist:
        messages.error(request, 'Adresy objednávky nejsou platné.')
        return redirect('start_order')

    cart = cart_order['cart']
    cart_items = [
        {
            'product_name': item.get('product_name', 'Produkt'),
            'quantity': item['quantity'],
            'price_per_item': item['price'],
            'total_price': item['quantity'] * item['price'],
        }
        for item in cart.values()
    ]

    total_price = sum(item['total_price'] for item in cart_items)

    return render(request, 'order_summary.html', {
        'shipping_address': shipping_address,
        'billing_address': billing_address,
        'cart_items': cart_items,
        'total_price': total_price,
    })


def confirm_order(request):
    cart_order = request.session.get('cart_order', None)

    if not cart_order:
        messages.error(request, 'Objednávka nemůže být provedena, protože není připravena.')
        return redirect('cart')

    try:
        shipping_address = Address.objects.get(id=cart_order['shipping_address_id'])
        billing_address = Address.objects.get(id=cart_order['billing_address_id'])
    except Address.DoesNotExist:
        messages.error(request, 'Adresy objednávky nejsou platné. Prosím zopakujte proces objednávky.')
        return redirect('start_order')

    cart = cart_order.get('cart', {})
    if not cart:
        messages.error(request, 'Košík je prázdný. Nelze potvrdit objednávku.')
        return redirect('cart')

    guest_email = request.POST.get('guest_email')
    if not guest_email and not request.user.is_authenticated:
        messages.error(request, 'Email je povinný pro neregistrované uživatele')
        return redirect('start_order')

    if not request.user.is_authenticated:
        request.session['guest_email'] = guest_email

    order = Order.objects.create(
        customer=request.user if request.user.is_authenticated else None,
        guest_email=guest_email,
        billing_address=billing_address,
        shipping_address=shipping_address,
        total_price=sum(item['quantity'] * item['price'] for item in cart.values())
    )

    for product_id, item in cart.items():
        OrderProduct.objects.create(
            order=order,
            product_id=product_id,
            quantity=item['quantity'],
            price_per_item=item['price'],
        )

    request.session.pop('cart_order', None)
    request.session.pop('cart', None)
    messages.success(request, f'Děkujeme za objednávku #{order.id}!')
    return redirect('thank_you', order_id=order.id)


def thank_you(request, order_id):
    if request.user.is_authenticated:
        order = get_object_or_404(Order, id=order_id, customer=request.user)
    else:
        guest_email = request.session.get('guest_email')
        if not guest_email:
            messages.error(request, 'Objednávka nenalezena. Hostující e-mail chybí.')
            return redirect('home')

        order = get_object_or_404(Order, id=order_id, guest_email=guest_email)

    items_with_totals = [
        {
            'product_name': item.product.product_name,
            'quantity': item.quantity,
            'price_per_item': item.price_per_item,
            'total_price': item.quantity * item.price_per_item,
        }
        for item in order.items.all()
    ]

    return render(request, 'thank_you.html', {
        'order': order,
        'items_with_totals': items_with_totals,
    })


@login_required
def my_orders(request):
    orders = Order.objects.filter(customer=request.user).order_by('-order_creation_datetime')
    return render(request, 'my_orders.html', {'orders': orders})


@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, customer=request.user)
    return render(request, 'order_detail.html', {'order': order})
