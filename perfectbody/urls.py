"""
URL configuration for perfectbody project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

from accounts.forms import TrainerBasicForm, TrainerServicesForm, TrainerDescriptionsForm, TrainerAddressForm, \
    TrainerProfileDescriptionForm
from manager.views import dashboard, add_product, approve_service, add_category, add_service, edit_product, \
    admin_dashboard, empty_categories, edit_category
from orders.views import start_order, order_summary, confirm_order, thank_you, my_orders, order_detail, cancel_order

from accounts.views import edit_profile, profile_view, change_password, register, login_view, \
    logout_view, TrainerRegistrationWizard, registration_success
from viewer.views import view_cart, add_to_cart, remove_from_cart, update_cart, home, products, product, services, \
    service, trainers, trainer, user_profile_view, search, update_cart_ajax
from accounts.views import edit_profile, profile_view, change_password, register, login_view, \
    logout_view
from viewer.views import view_cart, add_to_cart, remove_from_cart, update_cart, home, products, product, producer, \
    services, service, trainers, trainer, user_profile_view, search, update_cart_ajax

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('products/', products, name='products'),
    path('products/<pk>', products, name='products'),
    path('product/<pk>', product, name='product'),
    path('producer/<pk>', producer, name='producer'),
    path('services/', services, name='services'),
    path('services/<pk>', services, name='services'),
    path('service/<pk>', service, name='service'),
    path('trainers/', trainers, name='trainers'),
    path('trainer/<pk>', trainer, name='trainer'),
    path('register/', register, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('profile/', profile_view, name='profile'),
    path('edit_profile/', edit_profile, name='edit_profile'),
    path('cart/', view_cart, name='cart'),
    path('cart/add/<int:product_id>/', add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:product_id>/', remove_from_cart, name='remove_from_cart'),
    # path('cart/update/<int:product_id>/', update_cart, name='update_cart'),
    path('cart/update/<int:product_id>/', update_cart_ajax, name='update_cart_ajax'),
    path('change_password/', change_password, name='change_password'),
    path('user/<str:username>/', user_profile_view, name='user_profile'),
    path('start/', start_order, name='start_order'),
    path('summary/', order_summary, name='order_summary'),
    path('confirm/', confirm_order, name='confirm_order'),
    path('thank-you/<int:order_id>/', thank_you, name='thank_you'),
    path('my_orders/', my_orders, name='my_orders'),
    path('detail/<int:order_id>/', order_detail, name='order_detail'),
    path('orders/cancel/<int:order_id>/', cancel_order, name='cancel_order'),
    path('search/', search, name='search'),
    path(
        'register/trainer/',
        TrainerRegistrationWizard.as_view(
            form_list=[
                TrainerBasicForm,
                TrainerServicesForm,
                TrainerDescriptionsForm,
                TrainerProfileDescriptionForm,
                TrainerAddressForm
            ]
        ),
        name='trainer_register'
    ),
    path('register/success/', registration_success, name='registration_success'),
    path('dashboard', dashboard, name='dashboard'),
    path('add-product/', add_product, name='add_product'),
    path('add-category/', add_category, name='add_category'),
    path('add-service', add_service, name='add_service'),
    path('approve-service', approve_service, name='approve_service'),
    path('edit_product/<int:product_id>/', edit_product, name='edit_product'),
    path('dashboard/', admin_dashboard, name='admin_dashboard'),
    path('empty-categories/', empty_categories, name='empty_categories'),
    path('edit-category/<int:pk>', edit_category, name='edit_category'),


]
