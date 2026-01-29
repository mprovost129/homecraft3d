import stripe
from django.conf import settings
# sellers/views/dashboard.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from accounts.permissions import seller_required
from accounts.models import User
from sellers.models import Seller
from products.models import Product
from orders.models import Order, LineItem

@login_required
@seller_required
def dashboard(request):
    as_owner = request.GET.get('as_owner')
    if not hasattr(request.user, 'seller') and not (request.user.is_owner and as_owner):
        return redirect('/')

    if request.user.is_owner and as_owner:
        # Dummy context for owner viewing seller dashboard
        context = {
            'products': [],
            'orders': [],
            'total_sales': 0,
            'stripe_connected': False,
            'connect_url': None,
            'owner_viewing': True,
        }
        return render(request, 'sellers/dashboard.html', context)

    seller = request.user.seller
    products = Product.objects.filter(seller=seller)
    orders = LineItem.objects.filter(product__seller=seller)
    total_sales = sum([item.product.price * item.quantity for item in orders])
    digital_sales = sum([
        item.product.price * item.quantity for item in orders if item.product.is_digital
    ])
    material_sales = sum([
        item.product.price * item.quantity for item in orders if item.product.is_physical
    ])
    # Top products by sales
    from collections import Counter
    product_sales = Counter()
    for item in orders:
        product_sales[item.product.id] += item.quantity
    top_products = Product.objects.filter(id__in=[pid for pid, _ in product_sales.most_common(5)])
    # Recent reviews (using Rating model)
    from reviews.models import Rating
    recent_reviews = Rating.objects.filter(product__seller=seller).order_by('-created_at')[:5]
    # Sales trend (monthly)
    from django.db.models.functions import TruncMonth
    from django.db.models import Sum
    sales_trend = (
        orders.annotate(month=TruncMonth('order__created_at'))
        .values('month')
        .annotate(total=Sum('product__price'))
        .order_by('month')
    )
    sales_trend_labels = [item['month'].strftime('%b %Y') for item in sales_trend]
    sales_trend_data = [float(item['total']) if item['total'] else 0 for item in sales_trend]
    stripe_connected = bool(getattr(seller, 'stripe_account_id', ''))
    connect_url = None
    if not stripe_connected:
        # Create a Stripe Connect account link for onboarding
        if request.method == 'POST' and 'connect_stripe' in request.POST:
            account = stripe.Account.create(type='express')
            seller.stripe_account_id = account.id
            seller.save()
            link = stripe.AccountLink.create(
                account=account.id,
                refresh_url=request.build_absolute_uri(request.path),
                return_url=request.build_absolute_uri(request.path),
                type='account_onboarding',
            )
            return redirect(link.url)
        connect_url = True
    context = {
        'products': products,
        'orders': orders,
        'total_sales': total_sales,
        'digital_sales': digital_sales,
        'material_sales': material_sales,
        'top_products': top_products,
        'recent_reviews': recent_reviews,
        'sales_trend_labels': sales_trend_labels,
        'sales_trend_data': sales_trend_data,
        'stripe_connected': stripe_connected,
        'connect_url': connect_url,
    }
    return render(request, 'sellers/dashboard.html', context)
