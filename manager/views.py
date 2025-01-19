from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from unicodedata import category

from accounts.models import TrainersServices, UserProfile
from manager.forms import CategoryForm, ProductForm, ServiceForm, TrainerForm, ProducerForm, UserForm
from products.models import Product, Category, Producer, ProductReview, TrainerReview


def is_admin(user):
    return user.is_superuser or user.is_staff

def is_superuser(user):
    return user.is_superuser

@user_passes_test(is_admin)
def dashboard(request):
    return render(request,'dashboard.html')

@user_passes_test(is_admin)
def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Produkt byl úspěšně přidán.')
            return redirect('dashboard')
        else:
            messages.error(request, 'Chyba ve formuláři: Zkontrolujte zadané údaje.')
    else:
        form = ProductForm()
    return render(request,'add_product.html', {"form": form})

@user_passes_test(is_admin)
def add_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save()
            print(f"Kategorie byla vytvořena: {category.category_name}")
            return redirect('products')
        else:
            print(f"Chyba ve formuláři: {form.errors}")
    else:
        form = CategoryForm()

    return render(request, 'add_category.html', {'form': form})

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


@user_passes_test(is_admin)
def reject_service(request):
    if request.method == "POST":
        service_id = request.POST.get('service_id')
        if not service_id:
            messages.error(request, "Chybí ID služby.")
            return redirect('approve_service')

        try:
            service = TrainersServices.objects.get(id=service_id)
            service_name = service.service.product_name  # Uložení názvu služby pro zprávu
            service.delete()  # Odstranění služby z databáze
            messages.success(request, f"Služba '{service_name}' byla zamítnuta a odstraněna.")
        except TrainersServices.DoesNotExist:
            messages.error(request, "Služba s tímto ID neexistuje.")

        return redirect('approve_service')

    return redirect('approve_service')


@user_passes_test(is_admin)
def add_service(request):
    if request.method == 'POST':
        form = ServiceForm(request.POST)
        if form.is_valid():
            service = form.save(commit=False)
            service.producer = None
            service.save()
            messages.success(request, 'Služba byla úspěšně přidána jako service.')
            return redirect('services')
        else:
            messages.error(request, 'Chyba při přidávání služby. Zkontrolujte zadané údaje.')
    else:
        form = ServiceForm()

    context = {
        'form': form,
    }
    return render(request, 'add_service.html', context)

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
def all_categories(request):

    categories = Category.objects.all()

    for category in categories:
        category.view_url = reverse('products', args=[category.pk])
        category.edit_url = reverse('edit_category', args=[category.pk])

    return render(request, 'all_categories.html', {'categories': categories})


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
    category = get_object_or_404(Category, pk=pk)

    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, "Kategorie byla úspěšně upravena.")
            return redirect('dashboard')
    else:
        form = CategoryForm(instance=category)

    return render(request, 'edit_category.html', {'form': form, 'category': category})

@user_passes_test(is_admin)
def delete_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        product.delete()
        messages.success(request, f"Produkt '{product.product_name}' byl úspěšně smazán.")
        return redirect('dashboard')
    return render(request, 'delete_product.html', {"product": product})

@user_passes_test(is_admin)
def edit_service(request, service_id):
    service = get_object_or_404(Product, id=service_id, product_type='service')
    if request.method == 'POST':
        form = ServiceForm(request.POST, instance=service)
        if form.is_valid():
            form.save()
            messages.success(request, f"Služba '{service.product_name}' byla úspěšně upravena.")
            return redirect('manage_services')
        else:
            messages.error(request, 'Chyba při ukládání změn. Zkontrolujte zadané údaje.')
    else:
        form = ServiceForm(instance=service)
    return render(request, 'edit_service.html', {"form": form, "service": service})

@user_passes_test(is_admin)
def delete_service(request, service_id):
    service = get_object_or_404(Product, id=service_id, product_type='service')
    if request.method == 'POST':
        service.delete()
        messages.success(request, f"Služba '{service.product_name}' byla úspěšně smazána.")
        return redirect('manage_services')
    return render(request, 'delete_service.html', {"service": service})

@user_passes_test(is_admin)
def manage_products(request):
    products = Product.objects.filter(product_type='merchantdise')
    return render(request, 'manage_products.html', {'products': products})

@user_passes_test(is_admin)
def manage_services(request):
    services = Product.objects.filter(product_type='service')
    return render(request, 'manage_services.html', {'services': services})

@user_passes_test(is_admin)
def edit_trainer(request, trainer_id):
    trainer = get_object_or_404(UserProfile, id=trainer_id, is_staff=False)
    if request.method == 'POST':
        form = TrainerForm(request.POST, request.FILES, instance=trainer)
        if form.is_valid():
            form.save()
            messages.success(request, f"Trenér '{trainer.full_name()}' byl úspěšně upraven.")
            return redirect('trainers')
        else:
            messages.error(request, 'Chyba při ukládání změn. Zkontrolujte formulář.')
    else:
        form = TrainerForm(instance=trainer)
    return render(request, 'edit_trainer.html', {'form': form, 'trainer': trainer})

@user_passes_test(is_admin)
def delete_trainer(request, trainer_id):
    trainer = get_object_or_404(UserProfile, id=trainer_id, is_staff=False)
    if request.method == 'POST':
        trainer.delete()
        messages.success(request, f"Trenér '{trainer.full_name()}' byl úspěšně smazán.")
        return redirect('trainers')
    return render(request, 'delete_trainer.html', {'trainer': trainer})

@user_passes_test(is_admin)
def delete_category(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        category.delete()
        messages.success(request, f"Kategorie '{category.category_name}' byla úspěšně smazána.")
        return redirect('services')
    return redirect('services')

@user_passes_test(is_admin)
def edit_producer(request, pk):
    producer = get_object_or_404(Producer, pk=pk)
    if request.method == 'POST':
        form = ProducerForm(request.POST, instance=producer)
        if form.is_valid():
            form.save()
            messages.success(request, f"Výrobce '{producer.producer_name}' byl úspěšně upraven.")
            return redirect('producer', pk=pk)
        else:
            messages.error(request, 'Chyba při ukládání změn. Zkontrolujte formulář.')
    else:
        form = ProducerForm(instance=producer)
    return render(request, 'edit_producer.html', {'form': form, 'producer': producer})

@user_passes_test(is_admin)
def delete_producer(request, pk):
    producer = get_object_or_404(Producer, pk=pk)
    if request.method == 'POST':
        producer.delete()
        messages.success(request, f"Výrobce '{producer.producer_name}' byl úspěšně smazán.")
        return redirect('manage_producers')
    return redirect('producer', pk=pk)

@user_passes_test(is_admin)
def manage_producers(request):
    producers = Producer.objects.all()
    return render(request, 'manage_producers.html', {'producers': producers})

@user_passes_test(is_admin)
def add_producer(request):
    if request.method == 'POST':
        form = ProducerForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Výrobce byl úspěšně přidán.")
            return redirect('manage_producers')
        else:
            messages.error(request, "Chyba při přidávání výrobce. Zkontrolujte formulář.")
    else:
        form = ProducerForm()
    return render(request, 'add_producer.html', {'form': form})

@user_passes_test(is_admin)
def manage_users(request):
    users = UserProfile.objects.all()
    return render(request, 'manage_users.html', {'users': users})

@user_passes_test(is_admin)
def edit_user(request, user_id):
    user_to_edit = get_object_or_404(UserProfile, id=user_id)

    # Ověření, zda je uživatel ve skupině 'trainer'
    is_trainer = user_to_edit.groups.filter(name='trainer').exists()

    if not request.user.is_superuser and (user_to_edit.is_superuser or user_to_edit.is_staff):
        messages.error(request, "Nemáte oprávnění upravovat tohoto uživatele.")
        return redirect("manage_users")

    if request.method == "POST":
        form = UserForm(request.POST, instance=user_to_edit)
        if form.is_valid():
            form.save()
            messages.success(request, f"Uživatel '{user_to_edit.full_name()}' byl úspěšně upraven.")
            return redirect("manage_users")
    else:
        form = UserForm(instance=user_to_edit)

    return render(request, "edit_user.html", {
        "form": form,
        "user_to_edit": user_to_edit,
        "is_trainer": is_trainer,  # Použití proměnné pro šablonu
    })




@user_passes_test(is_admin)
def delete_user(request, user_id):
    user = get_object_or_404(UserProfile, id=user_id)
    if request.method == 'POST':
        user.delete()
        messages.success(request, "Uživatel byl úspěšně smazán.")
        return redirect('manage_users')
    return render(request, 'delete_user.html', {'user': user})

@user_passes_test(is_admin)
def approve_trainer_content(request):
    pending_trainers = UserProfile.objects.filter(
        Q(pending_trainer_short_description__isnull=False) |
        Q(pending_trainer_long_description__isnull=False)
    )
    pending_services = TrainersServices.objects.filter(
        pending_trainers_service_description__isnull=False
    )

    if request.method == "POST":
        content_type = request.POST.get("content_type")
        content_id = request.POST.get("content_id")
        action = request.POST.get("action")

        if content_type == "trainer_short_description":
            trainer = get_object_or_404(UserProfile, id=content_id)
            if action == "approve":
                trainer.trainer_short_description = trainer.pending_trainer_short_description
                trainer.pending_trainer_short_description = None
                trainer.save()
                messages.success(request, f"Krátký popis trenéra '{trainer.full_name()}' byl schválen.")
            elif action == "reject":
                trainer.pending_trainer_short_description = None
                trainer.save()
                messages.info(request, f"Krátký popis trenéra '{trainer.full_name()}' byl zamítnut.")

        elif content_type == "trainer_long_description":
            trainer = get_object_or_404(UserProfile, id=content_id)
            if action == "approve":
                trainer.trainer_long_description = trainer.pending_trainer_long_description
                trainer.pending_trainer_long_description = None
                trainer.save()
                messages.success(request, f"Dlouhý popis trenéra '{trainer.full_name()}' byl schválen.")
            elif action == "reject":
                trainer.pending_trainer_long_description = None
                trainer.save()
                messages.info(request, f"Dlouhý popis trenéra '{trainer.full_name()}' byl zamítnut.")

        elif content_type == "service":
            service = get_object_or_404(TrainersServices, id=content_id)
            if action == "approve":
                service.trainers_service_description = service.pending_trainers_service_description
                service.pending_trainers_service_description = None
                service.save()
                messages.success(request, f"Popis služby '{service.service.product_name}' byl schválen.")
            elif action == "reject":
                service.pending_trainers_service_description = None
                service.save()
                messages.info(request, f"Popis služby '{service.service.product_name}' byl zamítnut.")

        return redirect("approve_trainer_content")

    return render(request, "approve_trainer_content.html", {
        "pending_trainers": pending_trainers,
        "pending_services": pending_services,
    })


@login_required
def delete_product_review(request, review_id):

    # Ensure the user has admin permissions
    if not request.user.is_staff:
        messages.error(request, "Nemáte oprávnění smazat hodnocení.")
        return redirect('home')

    review = get_object_or_404(ProductReview, pk=review_id)

    product_name = review.product.product_name

    review.delete()
    messages.success(request, f"Hodnocení pro produkt '{product_name}' bylo úspěšně smazáno.")

    return redirect(request.META.get('HTTP_REFERER', 'home'))

@login_required
def delete_trainer_review(request, review_id):

    if not request.user.is_staff:
        messages.error(request, "Nemáte oprávnění smazat hodnocení.")
        return redirect('home')

    review = get_object_or_404(TrainerReview, pk=review_id)

    trainer_name = review.trainer.full_name()

    review.delete()
    messages.success(request, f"Hodnocení pro produkt '{trainer_name}' bylo úspěšně smazáno.")

    return redirect(request.META.get('HTTP_REFERER', 'home'))


@login_required
def delete_service_review(request, review_id):

    if not request.user.is_staff:
        messages.error(request, "Nemáte oprávnění smazat hodnocení.")
        return redirect('home')

    review = get_object_or_404(ProductReview, pk=review_id)
    service_name = review.product.product_name

    review.delete()
    messages.success(request, f"Hodnocení pro službu '{service_name}' bylo úspěšně smazáno.")

    return redirect(request.META.get('HTTP_REFERER', 'home'))

def service_details(request, service_id):

    service = get_object_or_404(TrainersServices, id=service_id)
    return render(request, 'service_details.html', {'service': service})