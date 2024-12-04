from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect

from perfectbody.settings import DEBUG
from accounts.forms import RegistrationForm, LoginForm


def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
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


