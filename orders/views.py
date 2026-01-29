# Order history view
from django.contrib.auth.decorators import login_required
from .models import Order

@login_required
def order_history_view(request):
    from reviews.models import Rating
    orders = Order.objects.filter(consumer=request.user).order_by('-created_at')
    for order in orders:
        for item in order.lineitem_set.all():
            # Check if the user has rated this product (by this seller) in this order
            item.seller_has_rating = Rating.objects.filter(product=item.product, user=request.user).exists()
    return render(request, 'orders/order_history.html', {'orders': orders})

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Order, LineItem, Download
from products.models import Product
from .forms import RefundRequestForm
from accounts.models_notification import Notification
from accounts.models import User
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse

@login_required
def consumer_dashboard(request):
    user = request.user
    orders = Order.objects.filter(consumer=user).order_by('-created_at')
    downloads = Download.objects.filter(line_item__order__consumer=user)
    recommendations = Product.objects.order_by('?')[:4]  # Simple random recs
    refund_form = None
    refund_requested = False
    # Example: Simulate order placement notification logic (replace with real order creation logic)
    if request.method == 'POST' and 'place_order' in request.POST:
        # Assume an order is created for demonstration
        order = Order.objects.filter(consumer=user).order_by('-created_at').first()
        if order:
            # Notify all sellers for products in the order
            for line in LineItem.objects.filter(order=order):
                product = line.product
                seller = getattr(product, 'seller', None)
                seller_user = getattr(seller, 'user', None)
                order_url = request.build_absolute_uri(reverse('order_history_view'))
                notif_message = f"You have a new order for your product '{product.name}'."
                if seller_user and seller_user != user:
                    # In-app notification
                    if getattr(seller_user, 'notify_orders_inapp', True):
                        Notification.objects.create(
                            user=seller_user,
                            message=notif_message,
                            url=order_url
                        )
                    # Email notification
                    if getattr(seller_user, 'notify_orders_email', True) and seller_user.email:
                        subject = f"New order for your product: {product.name}"
                        message = (
                            f"Hello {seller_user.username},\n\n"
                            f"You have received a new order for your product '{product.name}'.\n\n"
                            f"Order ID: {order.id}\n"
                            f"View order: {order_url}\n\n"
                            f"- The 3D Print Marketplace Team"
                        )
                        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [seller_user.email], fail_silently=True)
            # Notify consumer (buyer)
            if getattr(user, 'notify_orders_inapp', True):
                Notification.objects.create(
                    user=user,
                    message=f"Your order #{order.id} was placed successfully.",
                    url=order_url
                )
            if getattr(user, 'notify_orders_email', True) and user.email:
                subject = f"Order Confirmation: #{order.id}"
                message = (
                    f"Hello {user.username},\n\n"
                    f"Your order #{order.id} was placed successfully.\n\n"
                    f"View your order: {order_url}\n\n"
                    f"- The 3D Print Marketplace Team"
                )
                send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email], fail_silently=True)
        refund_form = RefundRequestForm()
    elif request.method == 'POST' and 'refund_order_id' in request.POST:
        refund_form = RefundRequestForm(request.POST)
        if refund_form.is_valid():
            # Here you would create a RefundRequest model or send an email
            refund_requested = True
    else:
        refund_form = RefundRequestForm()
    return render(request, 'orders/consumer_dashboard.html', {
        'orders': orders,
        'downloads': downloads,
        'recommendations': recommendations,
        'refund_form': refund_form,
        'refund_requested': refund_requested,
    })
