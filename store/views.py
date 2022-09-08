from django.shortcuts import render


# Create your views here.
def store(request):
    context = {}
    return render(request=request, template_name='store/store.html', context=context)


def cart(request):
    context = {}
    return render(request=request, template_name='store/cart.html', context=context)


def checkout(request):
    context = {}
    return render(request=request, template_name='store/checkout.html', context=context)
