import json
import datetime
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from . import models, utils


# Create your views here.
def store(request):
    data = utils.cart_data(request)
    cart_items = data['cartItems']

    products = models.Product.objects.all()
    context = {'products': products, 'cartItems': cart_items}
    return render(request=request, template_name='store/store.html', context=context)


def cart(request):
    data = utils.cart_data(request)
    cart_items = data['cartItems']
    order = data['order']
    items = data['items']

    context = {'items': items, 'order': order, 'cartItems': cart_items}
    return render(request=request, template_name='store/cart.html', context=context)


def checkout(request):
    data = utils.cart_data(request)
    cart_items = data['cartItems']
    order = data['order']
    items = data['items']

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

    else:
        customer, order = utils.guest_order(request, data)

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

    return JsonResponse('Payment completed', safe=False)
