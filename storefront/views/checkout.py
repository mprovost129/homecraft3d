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
    error = None
    if request.method == 'POST':
        # Stock validation
        for item in cart_items:
            product = item['product']
            quantity = item['quantity']
            # Only check stock for physical products
            if getattr(product, 'is_physical', False):
                if product.inventory is not None and quantity > product.inventory:
                    error = f"Not enough stock for {product.name}. Only {product.inventory} left."
                    break
        if not error:
            # Create order and line items
            order = Order.objects.create(consumer=request.user, status='Pending')
            for item in cart_items:
                LineItem.objects.create(order=order, product=item['product'], quantity=item['quantity'])
            request.session['cart'] = {}
            return redirect('order_confirmation', order_id=order.id)
    return render(request, 'storefront/checkout.html', {'cart_items': cart_items, 'total': total, 'error': error})

def order_confirmation_view(request, order_id):
    order = Order.objects.get(id=order_id)
    return render(request, 'storefront/order_confirmation.html', {'order': order})
