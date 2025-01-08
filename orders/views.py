import qrcode
import base64
from io import BytesIO
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q
from django.forms import modelform_factory

from accounts.models import Address
from orders.models import Order, OrderProduct

from django.db import transaction

from products.models import Product


def normalize_address_data(address_data):
    return {
        key: value.strip().lower() if isinstance(value, str) else value
        for key, value in address_data.items()
    }


def get_or_create_address(user, **address_data):
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



def get_initial_data(user, is_guest=False, guest_email=None):

    if user.is_authenticated:
        last_address = user.addresses.order_by('-id').first()
        return {
            'first_name': last_address.first_name if last_address else user.first_name,
            'last_name': last_address.last_name if last_address else user.last_name,
            'street': last_address.street if last_address else '',
            'street_number': last_address.street_number if last_address else '',
            'city': last_address.city if last_address else '',
            'postal_code': last_address.postal_code if last_address else '',
            'country': last_address.country if last_address else 'Česká republika',
            'email': last_address.email if last_address else user.email,
        }
    elif is_guest and guest_email:
        return {'email': guest_email}
    return {}


def start_order(request):
    cart = request.session.get('cart', {})
    if not cart:
        messages.error(request, 'Váš košík je prázdný.')
        return redirect('cart')

    AddressForm = modelform_factory(
        Address,
        fields=['first_name', 'last_name', 'street', 'street_number', 'city', 'postal_code', 'country']
    )

    email = None
    if not request.user.is_authenticated:
        email = request.session.get('guest_email', '')

    if request.method == 'POST':
        if not request.user.is_authenticated:
            email = request.POST.get('guest_email')

        shipping_form = AddressForm(request.POST, prefix='shipping')
        billing_form = (
            AddressForm(request.POST, prefix='billing') if 'different_billing' in request.POST else None
        )

        if shipping_form.is_valid() and (billing_form is None or billing_form.is_valid()):
            shipping_address = shipping_form.save(commit=False)
            if not request.user.is_authenticated:
                shipping_address.email = email
            shipping_address.user = request.user if request.user.is_authenticated else None
            shipping_address.save()

            billing_address = (
                billing_form.save(commit=False) if billing_form else shipping_address
            )
            if billing_form and not request.user.is_authenticated:
                billing_address.email = email
            if billing_form:
                billing_address.user = request.user if request.user.is_authenticated else None
                billing_address.save()

            if not request.user.is_authenticated:
                request.session['guest_email'] = email

            request.session['cart_order'] = {
                'shipping_address_id': shipping_address.id,
                'billing_address_id': billing_address.id,
                'cart': cart,
            }

            messages.success(request, 'Adresa byla úspěšně uložena.')
            return redirect('order_summary')

        messages.error(request, 'Vyplňte všechna povinná pole správně.')

    else:
        shipping_form = AddressForm(prefix='shipping')
        billing_form = AddressForm(prefix='billing') if not request.user.is_authenticated else None

    return render(request, 'start_order.html', {
        'shipping_address_form': shipping_form,
        'billing_address_form': billing_form,
        'guest_email': email,
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
        return redirect('start_order')

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

    guest_email = request.session.get('guest_email')
    if not guest_email and not request.user.is_authenticated:
        messages.error(request, 'Email je povinný pro neregistrované uživatele.')
        return redirect('start_order')

    # Použití transakce k zajištění integrity dat
    with transaction.atomic():
        # Vytvoření objednávky
        order = Order.objects.create(
            customer=request.user if request.user.is_authenticated else None,
            guest_email=guest_email,
            billing_address=billing_address,
            shipping_address=shipping_address,
            total_price=sum(item['quantity'] * item['price'] for item in cart.values())
        )

        # Odečet skladové zásoby a vytvoření položek objednávky
        for product_id, item in cart.items():
            product = get_object_or_404(Product, id=product_id)

            # Kontrola skladové dostupnosti
            if product.product_type == 'merchantdise' and product.stock_availability < item['quantity']:
                messages.error(request, f'Produkt {product.product_name} nemá dostatečnou skladovou zásobu.')
                return redirect('cart')

            # Odečtení zásoby pouze u produktů typu 'merchantdise'
            if product.product_type == 'merchantdise':
                product.stock_availability -= item['quantity']
                product.save()

            # Vytvoření položky objednávky
            OrderProduct.objects.create(
                order=order,
                product=product,
                quantity=item['quantity'],
                price_per_item=item['price'],
            )

    # Vymazání session
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

    formatted_order_id = str(order.id).zfill(8)

    bank_account = '123456789/0123'
    total_price = order.total_price
    variable_symbol = formatted_order_id

    payment_details = {
        'bank_account': bank_account,
        'variable_symbol': variable_symbol,
        'total_price': order.total_price,
    }

    #QRs
    qr_data = f"SPD*1.0*ACC:{bank_account}*AM:{total_price:.2f}*CC:CZK*X-VS:{variable_symbol}"
    qr_code_img = qrcode.make(qr_data)

    buffer = BytesIO()
    qr_code_img.save(buffer, format='PNG')
    buffer.seek(0)
    qr_code_base64 = base64.b64encode(buffer.read()).decode('utf-8')


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
        'formatted_order_id': formatted_order_id,
        'items_with_totals': items_with_totals,
        'payment_details': payment_details,
        'qr_code_base64': qr_code_base64,
    })


@login_required
def my_orders(request):
    orders = Order.objects.filter(customer=request.user).order_by('-order_creation_datetime')
    return render(request, 'my_orders.html', {'orders': orders})


@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, customer=request.user)
    return render(request, 'order_detail.html', {'order': order})

@login_required
def cancel_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, customer=request.user)

    if order.order_state != 'PENDING':
        messages.error(request, 'Tuto objednávku nelze zrušit.')
        return redirect('my_orders')

    # Vrácení skladové zásoby pro každý produkt v objednávce
    for item in order.items.all():
        product = item.product
        product.stock_availability += item.quantity
        product.save()

    # Aktualizace stavu objednávky
    order.order_state = 'CANCELLED'
    order.save()

    messages.success(request, f'Objednávka #{order.id} byla úspěšně zrušena a produkty byly vráceny na sklad.')
    return redirect('my_orders')
