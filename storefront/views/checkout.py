from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from products.models import Product
from orders.models import Order, LineItem

@login_required
def checkout_view(request):
    cart = request.session.get('cart', {})
    product_ids = cart.keys()
    products = Product.objects.filter(id__in=product_ids)
    cart_items = []
    total = 0
    for product in products:
        quantity = cart[str(product.id)]
        subtotal = float(product.price) * quantity
        cart_items.append({
            'product': product,
            'quantity': quantity,
            'subtotal': subtotal
        })
        total += subtotal
    if request.method == 'POST':
        # Create order and line items
        order = Order.objects.create(consumer=request.user, status='Pending')
        for item in cart_items:
            LineItem.objects.create(order=order, product=item['product'], quantity=item['quantity'])
        request.session['cart'] = {}
        return redirect('order_confirmation', order_id=order.id)
    return render(request, 'storefront/checkout.html', {'cart_items': cart_items, 'total': total})

def order_confirmation_view(request, order_id):
    order = Order.objects.get(id=order_id)
    return render(request, 'storefront/order_confirmation.html', {'order': order})
