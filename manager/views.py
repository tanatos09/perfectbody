from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect

from accounts.models import TrainersServices
from manager.forms import CategoryForm, ProductForm, ServiceForm
from products.models import Product, Category


def is_admin(user):
    return user.is_superuser or user.is_staff

@login_required
@user_passes_test(is_admin)
def dashboard(request):
    return render(request,'dashboard.html')

@login_required
@user_passes_test(is_admin)
def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = ProductForm()
        return render(request,'add_product.html', {"form": form})

@login_required
@user_passes_test(is_admin)
def add_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = CategoryForm()
        return render(request,'add_category.html', {"form": form})

@login_required
@user_passes_test(is_admin)
def approve_service(request):
    pending_services = TrainersServices.objects.filter(is_approved=False)
    if request.method == "POST":
        service_id = request.POST.get('service_id')
        service = TrainersServices.objects.get(id=service_id)
        service.is_approved = True
        service.save()
        return redirect('approve_service')
    return render(request, 'approve_service.html', {"pending_services": pending_services})

@login_required
@user_passes_test(is_admin)
def add_service(request):
    if request.method == 'POST':
        form = ServiceForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = ServiceForm()
    return render(request, 'add_service.html', {'form': form})

