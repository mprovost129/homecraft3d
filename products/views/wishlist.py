from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from products.models import Product
from products.models_wishlist import Wishlist

@login_required
def wishlist_view(request):
    wishlist, created = Wishlist.objects.get_or_create(user=request.user)
    return render(request, 'products/wishlist.html', {'wishlist': wishlist})

@login_required
def add_to_wishlist(request, product_id):
    wishlist, created = Wishlist.objects.get_or_create(user=request.user)
    product = Product.objects.get(id=product_id)
    wishlist.products.add(product)
    return redirect('wishlist')

@login_required
def remove_from_wishlist(request, product_id):
    wishlist, created = Wishlist.objects.get_or_create(user=request.user)
    product = Product.objects.get(id=product_id)
    wishlist.products.remove(product)
    return redirect('wishlist')
