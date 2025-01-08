from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from unicodedata import category

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
            category = form.save()
            print(f"Kategorie byla vytvořena: {category.category_name}")
            return redirect('products')
        else:
            print(f"Chyba ve formuláři: {form.errors}")  # Debugging chyb
    else:
        form = CategoryForm()

    return render(request, 'add_category.html', {'form': form})

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

@login_required
@user_passes_test(is_admin)
def edit_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            return redirect('product', product.pk)
    else:
        form = ProductForm(instance=product)
    return render(request, 'edit_product.html', {"form": form, "product": product})

@user_passes_test(lambda u: u.is_staff)
def admin_dashboard(request):

    categories = Category.objects.all()

    for category in categories:
        category.view_url = reverse('products', args=[category.pk])
        category.edit_url = reverse('edit_category', args=[category.pk])

    return render(request, 'admin_dashboard.html', {'categories': categories})


@user_passes_test(lambda u: u.is_staff)
def empty_categories(request):
    empty_categories = Category.objects.filter(
        Q(categories__isnull=True) & Q(subcategories__isnull=True)
    ).distinct()

    for category in empty_categories:
        category.view_url = reverse('products', args=[category.pk])
        category.edit_url = reverse('edit_category', args=[category.pk])

    return render(request, 'empty_categories.html', {'empty_categories': empty_categories})

def edit_category(request, pk):
    # Načtení kategorie podle ID
    category = get_object_or_404(Category, pk=pk)

    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, "Kategorie byla úspěšně upravena.")
            return redirect('admin_dashboard')
    else:
        form = CategoryForm(instance=category)

    return render(request, 'edit_category.html', {'form': form, 'category': category})
