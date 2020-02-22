from django.shortcuts import render
from django.http import HttpResponse
from .models import Product, Order, Customer

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
