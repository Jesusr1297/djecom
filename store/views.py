import json

from django.http import JsonResponse
from django.shortcuts import render
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
        items = []
        order = {'get_cart_total': 0, 'get_cart_items': 0, 'shipping': False}
        cart_items = 0
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


def process_order(request):
    print('data', request.body)
    return JsonResponse('Payment completed', safe=False)
