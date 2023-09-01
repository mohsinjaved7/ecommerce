from django.shortcuts import render,redirect,HttpResponse
from .models import *
from django.http import JsonResponse
import json
import datetime
from . utils import cookieCart,cartData,guestOrder
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout


# Create your views here.

def store(request):
    data = cartData(request)
    cartItems = data['cartItems']
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


def updateItem(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']
    print('Action:', action)
    print('Product:', productId)

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

    return JsonResponse('Item was Added', safe=False)


from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def processOrder(request):
    transaction_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)

    if request.user.is_authenticated:
        customer, created = Customer.objects.get_or_create(user=request.user, defaults={'name': request.user.username, 'email': request.user.email})
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
    else:
        customer, order = guestOrder(request, data)

    total = float(data['form']['total'])
    order.transaction_id = transaction_id

    if total == float(order.get_cart_total):
        order.complete = True
    order.save()

    if order.shipping:
        ShippingAddress.objects.create(
            customer=customer,
            order=order,
            address=data['shipping']['address'],
            city=data['shipping']['city'],
            state=data['shipping']['state'],
            zipcode=data['shipping']['zipcode'],
        )

    return JsonResponse('Payment completed', safe=False)


def Login(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        customer = authenticate(request,username=username,password=password)
        if customer is not None:
            login(request,customer)
            return redirect('store')
        else:
            return HttpResponse("Username or password doesn't match")

    return render(request,'store/login.html')


def SignUp(request):
    if request.method == "POST":
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        if password1 != password2:
            return HttpResponse("Your passwords don't match")
        else:
            # Create the User instance
            my_user = User.objects.create_user(username, email, password1)

            # Create the Customer instance and associate it with the User
            Customer.objects.create(user=my_user, name=username, email=email)

            return redirect('login')

    return render(request, 'store/signup.html')

def Logout(request):
    logout(request)
    return redirect('store')
