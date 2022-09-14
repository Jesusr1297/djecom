from django.shortcuts import render
from . import models


# Create your views here.
def store(request):
    products = models.Product.objects.all()
    context = {'products': products}
    return render(request=request, template_name='store/store.html', context=context)


def cart(request):
    context = {}
    return render(request=request, template_name='store/cart.html', context=context)


def checkout(request):
    context = {}
    return render(request=request, template_name='store/checkout.html', context=context)
