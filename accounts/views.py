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
    TrainerProfileDescriptionForm
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
def profile_view(request: HttpRequest) -> HttpResponse:
    user = request.user
    primary_address = None

    if hasattr(user, 'addresses') and user.addresses.exists():
        primary_address = user.addresses.order_by('-id').first()

    recent_orders = user.orders.all().order_by('-order_creation_datetime')[:5]


    return render(request, 'profile.html', {
        'user': user,
        'primary_address': primary_address,
        'recent_orders': recent_orders,
    })


@login_required
def edit_profile(request):
    user = request.user

    UserForm = UserEditForm
    AddressForm = modelform_factory(Address, fields=['first_name', 'last_name', 'street', 'street_number', 'city', 'postal_code', 'country', 'email'])

    last_shipping_address = user.addresses.order_by('-id').first()
    last_billing_address = None

    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=user)
        shipping_form = AddressForm(request.POST, instance=last_shipping_address, prefix='shipping')
        billing_form = AddressForm(request.POST, instance=last_billing_address, prefix='billing') if last_billing_address else None

        if user_form.is_valid() and shipping_form.is_valid() and (billing_form is None or billing_form.is_valid()):
            user_form.save()
            shipping_form.save()
            if billing_form:
                billing_form.save()
            messages.success(request, 'Profil byl úspěšně aktualizován.')
            return redirect('profile')
        else:
            messages.error(request, 'Došlo k chybě při aktualizaci profilu. Zkontrolujte zadané údaje.')
    else:
        user_form = UserForm(instance=user)
        shipping_form = AddressForm(instance=last_shipping_address, prefix='shipping')
        billing_form = AddressForm(instance=last_billing_address, prefix='billing') if last_billing_address else None

    return render(request, 'edit_profile.html', {
        'user_form': user_form,
        'shipping_form': shipping_form,
        'billing_form': billing_form,
    })



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
