import json
import datetime
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from . import models


# Create your views here.
def store(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = models.Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        cart_items = order.get_cart_items
    else:
        items = []
        order = {'get_cart_total': 0, 'get_cart_items': 0, 'shipping': False}
        cart_items = order['get_cart_items']

    products = models.Product.objects.all()
    context = {'products': products, 'cartItems': cart_items}
    return render(request=request, template_name='store/store.html', context=context)


def cart(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = models.Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        cart_items = order.get_cart_items
    else:
        try:
            cart = json.loads(request.COOKIES['cart'])
        except KeyError:
            cart = {}
        items = []
        order = {'get_cart_total': 0, 'get_cart_items': 0, 'shipping': False}
        cart_items = 0

        for i in cart:
            cart_items += cart[i]['quantity']
            product = models.Product.objects.get(id=i)
            total = product.price * cart[i]['quantity']

            order['get_cart_total'] += total
            order['get_cart_items'] += cart[i]['quantity']

            item = {
                'product': {
                    'id': product.id,
                    'name': product.name,
                    'price': product.price,
                    'image_url': product.image_url
                },
                'quantity': cart[i]['quantity'],
                'get_total': total
            }

            items.append(item)

    context = {'items': items, 'order': order, 'cartItems': cart_items}
    return render(request=request, template_name='store/cart.html', context=context)


def checkout(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = models.Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        cart_items = order.get_cart_items
    else:
        items = []
        order = {'get_cart_total': 0, 'get_cart_items': 0, 'shipping': False}
        cart_items = 0
    context = {'items': items, 'order': order, 'cartItems': cart_items}
    return render(request=request, template_name='store/checkout.html', context=context)


def update_item(request):
    data = json.loads(request.body)
    product_id = data['productId']
    action = data['action']

    print('Action: ', action)
    print('productId', product_id)

    customer = request.user.customer
    product = models.Product.objects.get(id=product_id)
    order, created = models.Order.objects.get_or_create(customer=customer, complete=False)
    order_item, created = models.OrderItem.objects.get_or_create(order=order, product=product)

    if action == 'add':
        order_item.quantity += 1
    elif action == 'remove':
        order_item.quantity -= 1
    order_item.save()

    if order_item.quantity <= 0:
        order_item.delete()
    return JsonResponse('Item was added', safe=False)


@csrf_exempt
def process_order(request):
    transaction_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = models.Order.objects.get_or_create(customer=customer, complete=False)
        total = float(data['form']['total'])
        order.transaction_id = transaction_id

        if total == order.get_cart_total:
            order.complete = True
        order.save()

        if order.shipping:
            models.ShippingAddress.objects.create(
                customer=customer,
                order=order,
                address=data['shipping']['address'],
                state=data['shipping']['state'],
                city=data['shipping']['city'],
                zip_code=data['shipping']['zipcode'],

            )

    else:
        print('user not logged in')
    return JsonResponse('Payment completed', safe=False)
