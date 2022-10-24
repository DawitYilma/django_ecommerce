from itertools import product
from django.shortcuts import render
from django.http import Http404, JsonResponse
import json
import datetime
from ecommerce.forms import CustomerForm

from .models import *
from .utils import cookieCart, cartData, guestOrder

from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.contrib.auth.decorators import login_required

# Create your views here.

def store(request):
    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']

    products = Product.objects.all()
    context = {'products': products, 'cartItems': cartItems}
    return render(request, 'store/store.html', context)

def cart(request):
    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']

    context = {'items': items, 'order': order, 'cartItems': cartItems}
    return render(request, 'store/cart.html', context)

def checkout(request):
    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']
    context = {'items': items, 'order': order, 'cartItems': cartItems}
    return render(request, 'store/checkout.html', context)

def product(request, name):
    data = cartData(request)
    cartItems = data['cartItems']
    try:
        product = Product.objects.get(name=name)
    except:
        raise Http404
    context = {
        'product': product,
        'cartItems': cartItems
        }
    return render(request, 'store/product.html', context)

def register(request):
    data = cartData(request)
    cartItems = data['cartItems']

    registered = False

    if request.method == "POST":
        customer_form = CustomerForm(data=request.POST)

        if customer_form.is_valid():
            customer = customer_form.save()
            customer.set_password(customer.password)
            customer.save()
            create = Customer.objects.create(user=customer, name=customer.username, email=customer.email)
            registered = True
            return HttpResponseRedirect(reverse('customer_login'))
        else:
            print(customer_form.errors)
    else:
        customer_form = CustomerForm()
    context = {'cartItems': cartItems, 'customer_form': customer_form,
                            'registered': registered}
    
    return render(request, 'store/registration.html', context)
def customer_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse('store'))

def customer_login(request):
    data = cartData(request)
    cartItems = data['cartItems']
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        customer = authenticate(username=username, password=password)
        
        if customer:
            if customer.is_active:
                login(request, customer)

                return HttpResponseRedirect(reverse('store'))
            else:
                return HttpResponse("Account Is Not Active")
        else:
            return HttpResponse('Invalid login details supplied!')
    else:
        context = {'cartItems': cartItems,}
        return render(request, 'store/login.html', context)

def updateItem(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']

    customer = request.user.customer
    product = Product.objects.get(id=productId)
    order, created = Order.objects.get_or_create(customer=customer, complete=False)
    orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)

    if action == 'add':
        orderItem.quantity = (orderItem.quantity + 1)
    elif action == 'remove':
        orderItem.quantity = (orderItem.quantity - 1)
    
    orderItem.save()

    if orderItem.quantity <= 0:
        orderItem.delete()

    return JsonResponse('Item was added', safe=False)

def processOrder(request):
    transaction_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        
    else:
        customer, order = guestOrder(request, data)

    total = float(data['form']['total'])
    order.transaction_id = transaction_id

    if total == order.get_cart_total:
        order.complete = True
    order.save()

    if order.shipping == True:
            ShippingAddress.objects.create(
                customer = customer,
                order = order,
                address = data['shipping']['address'],
                city = data['shipping']['city'],
                state = data['shipping']['state'],
                zipcode = data['shipping']['zipcode']
            )

    return JsonResponse('Payment Complete', safe=False)
