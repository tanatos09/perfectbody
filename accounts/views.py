from sqlite3 import IntegrityError

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect

from perfectbody.settings import DEBUG
from accounts.forms import RegistrationForm, LoginForm


def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            try:
                form.save()
                return redirect('home')
            except IntegrityError:
                form.add_error(None, 'Došlo k chybě. Zkontrolujte zadaná data')
        else:
            form.add_error(None, 'Ověřte správnost údajů')
    else:
        form = RegistrationForm()
    return render(request, 'register.html', {"form": form})

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                if DEBUG:
                    print('Uspesne prihlaseni')
                return redirect('home')
            else:
                messages.error(request, 'Neplatné uživatelské jméno nebo heslo.')
    else:
        form = LoginForm()
    return render(request, 'login.html', {"form": form})

def logout_view(request):
    logout(request)
    messages.success(request, 'Byl(a) jste úspěšně odhlášen(a)')
    return redirect('home')

