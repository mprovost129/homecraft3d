from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from products.models import Product

# Simple session-based cart

def cart_view(request):
    cart = request.session.get('cart', {})
    product_ids = cart.keys()
    products = Product.objects.filter(id__in=product_ids)
    cart_items = []
    for product in products:
        cart_items.append({
            'product': product,
            'quantity': cart[str(product.pk)]
        })
    return render(request, 'storefront/cart.html', {'cart_items': cart_items})

def add_to_cart(request, product_id):
    cart = request.session.get('cart', {})
    cart[str(product_id)] = cart.get(str(product_id), 0) + 1
    request.session['cart'] = cart
    return redirect('cart')

def remove_from_cart(request, product_id):
    cart = request.session.get('cart', {})
    if str(product_id) in cart:
        del cart[str(product_id)]
    request.session['cart'] = cart
    return redirect('cart')
