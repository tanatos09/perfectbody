import logging

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.messages import get_messages
from django.forms import modelformset_factory
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect

from accounts.forms import RegistrationForm, LoginForm, UserEditForm, PasswordChangeForm, TrainerRegistrationForm, \
    AddressForm
from accounts.models import Address

logger = logging.getLogger(__name__)

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

def trainer_register(request):
    if request.method == 'POST':
        form = TrainerRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Registrace trenéra proběhla úspěšně. Nyní se můžete přihlásit')
            return redirect('login')
    else:
        form = TrainerRegistrationForm
    return render(request, 'trainer_register.html', {'form': form})


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
    primary_address = None
    if hasattr(request.user, 'addresses') and request.user.addresses.exists():
        primary_address = request.user.addresses.order_by('-id').first()
    return render(request, 'profile.html', {'user': request.user, 'primary_address': primary_address})

@login_required
def edit_profile(request):
    user = request.user
    AddressFormSet = modelformset_factory(Address, form=AddressForm, extra=0, can_delete=True)

    if request.method == 'POST':
        user_form = UserEditForm(request.POST, instance=user)
        address_formset = AddressFormSet(
            request.POST,
            queryset=Address.objects.filter(user=user),
            prefix='addresses'
        )


        if user_form.is_valid() and address_formset.is_valid():
            user_form.save()

            for form in address_formset:
                if form.cleaned_data and not form.cleaned_data.get('DELETE'):
                    address = form.save(commit=False)
                    address.user = user
                    address.save()
                elif form.cleaned_data.get('DELETE'):
                    form.instance.delete()

            messages.success(request, 'Vaše údaje byly úspěšně aktualizovány.')
            return redirect('profile')
        else:
            messages.error(request, 'Došlo k chybě při aktualizaci profilu.')
    else:
        queryset = Address.objects.filter(user=user)
        if not queryset.exists():
            AddressFormSet.extra = 1
        address_formset = AddressFormSet(queryset=queryset, prefix='addresses')
        user_form = UserEditForm(instance=user)

    return render(request, 'edit_profile.html', {
        "form": user_form,
        'address_formset': address_formset
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
