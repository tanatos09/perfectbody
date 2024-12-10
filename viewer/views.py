from django.shortcuts import render

from products.models import Product


def home(request):
    return render(request, 'home.html')

def products(request):
    return render(request, 'products.html')

def products(request):
    products = Product.objects.filter(product_type='merchantdise')
    print(products)
    return render(request, 'products.html', {'products': products})

def services(request):
    products = Product.objects.filter(product_type='service')
    return render(request, 'services.html', {"products": products})

def trainers(request):
    return render(request, 'trainers.html')

