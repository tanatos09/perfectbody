from django.http import HttpResponse
from django.shortcuts import render
from products.models import Product

def home(request):
    return render(request, 'home.html')

def products(request):
    products_list = Product.objects.filter(product_type="merchantdise")
    context = {'products': products_list}
    return render(request, "products.html", context)

def product(request, pk):
    if Product.objects.filter(id=pk) and Product.objects.filter(product_type="merchantdise"):
        product_detail = Product.objects.get(id=pk)
        context = {'product': product_detail}
        return render(request, "product.html", context)
    return products(request)

def services(request):
    services_list = Product.objects.filter(product_type="service")
    context = {'services': services_list}
    return render(request, "services.html", context)

def service(request, pk):
    if Product.objects.filter(id=pk) and Product.objects.filter(product_type="service"):
        service_detail = Product.objects.get(id=pk)
        context = {'service': service_detail}
        return render(request, "service.html", context)
    return products(request)

def trainers(request):
    return render(request, 'trainers.html')
