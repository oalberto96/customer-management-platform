from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.forms import inlineformset_factory
from .models import Product, Order, Customer
from .forms import OrderForm


def get_customers_orders():
    customers = Customer.objects.all()
    customers_orders_count = []
    for customer in customers:
        customers_orders_count.append({
            'customer': customer,
            'orders_count': customer.order_set.all().count()
        })
    return customers_orders_count
    

# Create your views here.
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

def products(request):
    products = Product.objects.all()
    context = {
        'products': products
    }
    return render(request, 'accounts/products.html', context)

def customer(request, pk):
    customer = Customer.objects.get(id=pk)
    orders = customer.order_set.all()
    context = {
        'customer': customer,
        'orders': orders,
        'orders_count': orders.count()
    }
    return render(request, 'accounts/customer.html', context)

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

def delete_order(request, pk):
    order = Order.objects.get(id=pk)
    if request.method == 'POST':
        order.delete()
        return redirect('home')
    context = {
        'item': order
    }
    return render(request, 'accounts/delete.html', context)