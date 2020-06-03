from django.shortcuts import render, redirect
from django.forms import formset_factory, inlineformset_factory  # creates multiple forms in one form
from django.http import HttpResponse
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group

# Create your views here.

from .decorators import unauthenticated_user, allowed_users, admin_only
from .filters import OrderFilter
from .models import *
from .forms import OrderForm, CreateUserForm, CustomerForm


@unauthenticated_user
def register_page(request):
    form = CreateUserForm()
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, 'Account was created for ' + username)
            return redirect('login')

    context_dict = {
        'form': form,
    }
    return render(request, 'accounts/register.html', context=context_dict)


@unauthenticated_user
def login_page(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.info(request, 'Username or Password is incorrect')

    context_dict = {

    }
    return render(request, 'accounts/login.html', context=context_dict)


def logout_page(request):
    logout(request)
    return redirect('login')


@login_required(login_url='login')  # decorator redirects one to the login page if they try to access this page
@admin_only
def home(request):
    orders = Order.objects.all()
    total_orders = orders.count()
    pending_orders = orders.filter(status='Pending').count()
    delivered_orders = orders.filter(status='Delivered').count()

    customers = Customer.objects.all()

    context_dict = {
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'delivered_orders': delivered_orders,
        'customers': customers,
        'orders': orders,
    }
    return render(request, 'accounts/dashboard.html', context=context_dict)


@login_required(login_url='login')
@allowed_users(allowed_roles=['customer'])  # decorator ensures only an admin can log in into this page
def user_page(request):
    orders = request.user.customer.order_set.all()

    total_orders = orders.count()
    pending_orders = orders.filter(status='Pending').count()
    delivered_orders = orders.filter(status='Delivered').count()

    context_dict = {
        'orders': orders,
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'delivered_orders': delivered_orders,
    }
    return render(request, 'accounts/users.html', context=context_dict)


@login_required(login_url='login')
@allowed_users(allowed_roles=['customer'])  # decorator ensures only an admin can log in into this page
def account_settings(request):
    customer = request.user.customer  # gets current logged in customer
    form = CustomerForm(instance=customer)

    if request.method == 'POST':
        form = CustomerForm(request.POST, request.FILES, instance=customer)
        if form.is_valid():
            form.save()
            # return redirect('account')
    context_dict = {
        'form': form,
    }
    return render(request, 'accounts/account_settings.html', context=context_dict)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])  # decorator ensures only an admin can log in into this page
def products(request):
    products = Product.objects.all()
    context_dict = {
        'products': products,
    }
    return render(request, 'accounts/products.html', context=context_dict)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def customers(request, pk):
    customer = Customer.objects.get(id=pk)

    orders = customer.order_set.all()
    total_orders = orders.count()

    myfilter = OrderFilter(request.GET, queryset=orders)
    orders = myfilter.qs

    context_dict = {
        'customer': customer,
        'orders': orders,
        'total_orders': total_orders,
        'myfilter': myfilter,
    }
    return render(request, 'accounts/customers.html', context=context_dict)


@login_required(login_url='login')  # decorator redirects one to the login page if they try to access this page
@allowed_users(allowed_roles=['admin'])  # decorator ensures only an admin can log in into this page
def create_order(request, pk):
    OrderFormSet = inlineformset_factory(Customer, Order, fields=('product', 'status'), extra=5)
    customer = Customer.objects.get(id=pk)
    # form = OrderForm(initial={'customer': customer})
    formset = OrderFormSet(queryset=Order.objects.none(), instance=customer)
    if request.method == 'POST':
        # form = OrderForm(request.POST)
        formset = OrderFormSet(request.POST, instance=customer)
        if formset.is_valid():
            formset.save()
            return redirect('/')

    context_dict = {
        'formset': formset,
        # 'customer': customer,
    }
    return render(request, 'accounts/order_form.html', context=context_dict)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def update_order(request, pk):
    order = Order.objects.get(id=pk)
    form = OrderForm(instance=order)  # prefills the form to be updated
    if request.method == 'POST':
        form = OrderForm(request.POST, instance=order)  # this enables the form to be saved only in this instance
        # not as a new form
        if form.is_valid():
            form.save()
            return redirect('/')
    context_dict = {
        'form': form,
    }
    return render(request, 'accounts/order_form.html', context=context_dict)


@login_required(login_url='login')  # decorator redirects one to the login page if they try to access this page
@allowed_users(allowed_roles=['admin'])  # decorator ensures only an admin can log in into this page
def delete_order(request, pk):
    order = Order.objects.get(id=pk)
    if request.method == 'POST':
        order.delete()
        return redirect('/')
    context_dict = {
        'item': order,
    }
    return render(request, 'accounts/delete.html', context=context_dict)
