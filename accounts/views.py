import logging

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.contrib.messages import get_messages
from django.db import IntegrityError
from django.forms import modelformset_factory, modelform_factory
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from formtools.wizard.views import SessionWizardView

from accounts.forms import RegistrationForm, LoginForm, UserEditForm, PasswordChangeForm, TrainerRegistrationForm, \
    AddressForm, TrainerBasicForm, TrainerServicesForm, TrainerDescriptionsForm, TrainerAddressForm, \
    TrainerProfileDescriptionForm, TrainerServiceDescriptionsForm
from accounts.models import Address, UserProfile, TrainersServices

logger = logging.getLogger(__name__)

class TrainerRegistrationWizard(SessionWizardView):
    template_name = "trainer_register.html"
    form_list = [
        TrainerBasicForm,
        TrainerServicesForm,
        TrainerDescriptionsForm,
        TrainerProfileDescriptionForm,
        TrainerAddressForm
    ]

    def get_form_kwargs(self, step):
        kwargs = super().get_form_kwargs(step)
        if step == '2':
            previous_data = self.get_cleaned_data_for_step('1')
            if previous_data:
                kwargs['selected_services'] = previous_data['services']
        return kwargs

    def done(self, form_list, **kwargs):
        forms = [form.cleaned_data for form in form_list]

        # Uložení uživatele
        user = UserProfile(
            username=forms[0]['username'],
            first_name=forms[0]['first_name'],
            last_name=forms[0]['last_name'],
            email=forms[0]['email'],
            phone=forms[0]['phone'],
            date_of_birth=forms[0]['date_of_birth'],
            trainer_short_description=forms[3]['trainer_short_description'],  # Použití správného indexu
            trainer_long_description=forms[3]['trainer_long_description']  # Použití správného indexu
        )
        user.set_password(forms[0]['password'])
        user.save()

        # Přiřazení do skupiny `trainer`
        trainer_group, _ = Group.objects.get_or_create(name='trainer')
        user.groups.add(trainer_group)

        # Uložení schválených služeb
        selected_services = forms[1]['services']
        descriptions = forms[2]  # Popisy služeb jsou v kroku 3
        for service in selected_services:
            description_key = f'description_{service.id}'
            TrainersServices.objects.create(
                trainer=user,
                service=service,
                trainers_service_description=descriptions[description_key],
                is_approved=False
            )

        # Přesměrování na stránku úspěšné registrace
        return redirect('registration_success')

def registration_success(request):
    return render(request, 'registration_success.html')

def clear_messages(request: HttpRequest):
    storage = get_messages(request)
    for _ in storage:
        pass

def register(request: HttpRequest) -> HttpResponse:
    clear_messages(request)

    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, "Registrace proběhla úspěšně. Nyní se můžete přihlásit.")
                return redirect('login')
            except Exception as e:
                logger.error(f"Neočekávaná chyba při registraci: {e}", exc_info=True)
                messages.error(request, "Došlo k neočekávané chybě. Zkuste to znovu.")
        else:
            messages.warning(request, "Údaje nejsou platné. Zkontrolujte a zkuste znovu.")
    else:
        form = RegistrationForm()

    return render(request, 'register.html', {"form": form})

def login_view(request: HttpRequest) -> HttpResponse:
    clear_messages(request)
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                messages.success(request, f"Vítejte, {username}!")
                redirect_to = request.GET.get('next', 'home')
                return redirect(redirect_to)
            else:
                logger.warning(f"Neplatné přihlašovací údaje pro uživatele: {form.cleaned_data.get('username')}")
                messages.error(request, "Neplatné uživatelské jméno nebo heslo.")
        else:
            messages.warning(request, "Zadané údaje nejsou platné.")
    else:
        form = LoginForm()

    return render(request, 'login.html', {"form": form})


def logout_view(request: HttpRequest) -> HttpResponse:
    clear_messages(request)
    logout(request)
    messages.success(request, "Byl(a) jste úspěšně odhlášen(a).")
    return redirect('login')
@login_required
def profile_view(request):
    user = request.user
    is_trainer = user.groups.filter(name='trainer').exists()

    # Schválené služby pro trenéra
    approved_services = []
    if is_trainer:
        approved_services = TrainersServices.objects.filter(trainer=user, is_approved=True).select_related('service')

    # Primární adresa uživatele
    primary_address = None
    if hasattr(user, 'addresses') and user.addresses.exists():
        primary_address = user.addresses.order_by('-id').first()

    # Nedávné objednávky
    recent_orders = user.orders.all().order_by('-order_creation_datetime')[:5]

    return render(request, 'profile.html', {
        'user': user,
        'is_trainer': is_trainer,
        'approved_services': approved_services,
        'primary_address': primary_address,
        'recent_orders': recent_orders,
    })


@login_required
def edit_profile(request):
    user = request.user

    user_form = UserEditForm(instance=user)

    last_shipping_address = user.addresses.order_by('-id').first()
    initial_data = None
    if last_shipping_address:
        initial_data = {
            'first_name': last_shipping_address.first_name,
            'last_name': last_shipping_address.last_name,
            'street': last_shipping_address.street,
            'street_number': last_shipping_address.street_number,
            'city': last_shipping_address.city,
            'postal_code': last_shipping_address.postal_code,
            'country': last_shipping_address.country,
            'email': last_shipping_address.email,
        }

    shipping_form = AddressForm(initial=initial_data)

    TrainerForm = TrainerProfileDescriptionForm
    ServiceDescriptionsForm = TrainerServiceDescriptionsForm

    approved_services = TrainersServices.objects.filter(trainer=user, is_approved=True).select_related("service")

    trainer_form = TrainerForm(instance=user, initial={
        "pending_trainer_short_description": user.pending_trainer_short_description or user.trainer_short_description,
        "pending_trainer_long_description": user.pending_trainer_long_description or user.trainer_long_description,
        "pending_profile_picture": user.pending_profile_picture or user.profile_picture,
    })
    service_form = ServiceDescriptionsForm(services=approved_services)

    if request.method == "POST":
        form_type = request.POST.get("form_type")

        if form_type == "trainer_form":
            trainer_form = TrainerForm(request.POST, instance=user)
            if trainer_form.is_valid():
                user.pending_trainer_short_description = trainer_form.cleaned_data.get("pending_trainer_short_description")
                user.pending_trainer_long_description = trainer_form.cleaned_data.get("pending_trainer_long_description")
                user.pending_profile_picture = trainer_form.cleaned_data.get("pending_profile_picture")
                user.save()
                messages.success(request, "Změny v profilu trenéra byly uloženy a čekají na schválení.")
                return redirect("edit_profile")
            else:
                messages.error(request, "Opravit chyby ve formuláři trenéra.")

        elif form_type == "service_form":
            service_form = ServiceDescriptionsForm(request.POST, services=approved_services)
            if service_form.is_valid():
                for service in approved_services:
                    description_field = f"description_{service.id}"
                    service.pending_trainers_service_description = service_form.cleaned_data.get(description_field)
                    service.save()
                messages.success(request, "Změny v popiscích služeb byly uloženy a čekají na schválení.")
                return redirect("edit_profile")
            else:
                messages.error(request, "Opravit chyby v popiscích služeb.")

        elif form_type == "user_form":
            user_form = UserEditForm(request.POST, instance=user)
            if user_form.is_valid():
                user_form.save()
                messages.success(request, "Osobní údaje byly úspěšně aktualizovány.")
                return redirect("edit_profile")
            else:
                messages.error(request, "Opravit chyby v osobních údajích.")

        elif form_type == "shipping_form":
            shipping_form = AddressForm(request.POST)
            if shipping_form.is_valid():
                address = shipping_form.save(commit=False)
                address.user = user
                address.save()
                messages.success(request, "Doručovací adresa byla úspěšně aktualizována.")
                return redirect("edit_profile")
            else:
                messages.error(request, "Opravit chyby v doručovací adrese.")

    context = {
        "trainer_form": trainer_form,
        "service_form": service_form,
        "user_form": user_form,
        "shipping_form": shipping_form,
        "approved_services": approved_services,
        "is_trainer": user.groups.filter(name="trainer").exists(),
    }
    return render(request, "edit_profile.html", context)




@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, request.user)
            messages.success(request, 'Vaše heslo bylo změněno')
            return redirect('profile')
        else:
            messages.error(request, 'Heslo nebylo změněno. Opravte chyby a zkuste to znovu')
    else: form = PasswordChangeForm(request.user)

    return render(request, 'change_password.html', {'form': form})
