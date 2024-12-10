from django.http import HttpResponse
from django.shortcuts import render
from products.models import Product

def home(request):
    return render(request, 'home.html')

def products(request):
    products_list = Product.objects.filter(product_type="merchantdise")
    context = {'products': products_list}
    return render(request, "products.html", context)

def services(request):
    services_list = Product.objects.filter(product_type="service")
    context = {'services': services_list}
    return render(request, "services.html", context)

def trainers(request):
    return render(request, 'trainers.html')

