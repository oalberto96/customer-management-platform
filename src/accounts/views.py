from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.forms import inlineformset_factory
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .decorators import unauthenticated_user, allowed_users, admin_only
from .models import Product, Order, Customer
from .forms import OrderForm, CreateUserForm
from .filters import OrderFilter


@unauthenticated_user
def login_page(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('home')
        else:
            messages.info(request, 'Username or password is incorrect')
    context = {}
    return render(request, 'accounts/login.html', context)

@unauthenticated_user
def register_page(request):
    form = CreateUserForm()
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            form.save()
            user = form.cleaned_data.get('username')
            messages.success(request, 'Account was created for ' + user)
            return redirect('login')
    context = {'form': form}
    return render(request, 'accounts/register.html', context)

def get_customers_orders():
    customers = Customer.objects.all()
    customers_orders_count = []
    for customer in customers:
        customers_orders_count.append({
            'customer': customer,
            'orders_count': customer.order_set.all().count()
        })
    return customers_orders_count

def logout_user(request): 
    logout(request)
    return redirect('login')
    

# Create your views here.
@login_required(login_url='login')
@admin_only
def home(request):
    orders = Order.objects.all()
    context = {
        'last_5_orders': orders[:5],
        'customers_orders': get_customers_orders(),
        'total_orders': orders.count(),
        'orders_delivered': orders.filter(status='Delivered').count(),
        'orders_pending': orders.filter(status='Pending').count()
    }
    return render(request, 'accounts/dashboard.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def products(request):
    products = Product.objects.all()
    context = {
        'products': products
    }
    return render(request, 'accounts/products.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def customer(request, pk):
    customer = Customer.objects.get(id=pk)
    orders = customer.order_set.all()
    my_filter = OrderFilter(request.GET, queryset=orders)
    orders = my_filter.qs
    context = {
        'customer': customer,
        'orders': orders,
        'orders_count': orders.count(),
        'my_filter': my_filter
    }
    return render(request, 'accounts/customer.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def create_order(request, pk):
    OrderFormSet = inlineformset_factory(Customer, Order, fields=('product', 'status'), extra=2)
    customer = Customer.objects.get(id=pk)
    formset = OrderFormSet(
        queryset=Order.objects.none(),
        instance=customer,
    )
    # form = OrderForm(initial={
    #     'customer': customer
    # })
    if request.method == 'POST':
        formset = OrderFormSet(request.POST, instance=customer)
        if formset.is_valid():
            formset.save()
            return redirect('home')
    context = {'formset': formset}
    return render(request, 'accounts/order_form.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def update_order(request, pk):
    order = Order.objects.get(id=pk)
    form = OrderForm(instance=order)
    if request.method == 'POST':
        form = OrderForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            return redirect('home')
    context = {'form': form}
    return render(request, 'accounts/order_form.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def delete_order(request, pk):
    order = Order.objects.get(id=pk)
    if request.method == 'POST':
        order.delete()
        return redirect('home')
    context = {
        'item': order
    }
    return render(request, 'accounts/delete.html', context)