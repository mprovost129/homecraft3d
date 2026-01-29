# Checkout and order confirmation views
from products.models import Product, Category
from ..models import StorefrontSettings
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
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
        # Use product.pk instead of product.id to ensure compatibility with custom primary keys
        quantity = cart[str(product.pk)]
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
        return redirect('order_confirmation', order_id=order.pk)
    return render(request, 'storefront/checkout.html', {'cart_items': cart_items, 'total': total})

def order_confirmation_view(request, order_id):
    order = Order.objects.get(id=order_id)
    return render(request, 'storefront/order_confirmation.html', {'order': order})
# from django.shortcuts import render  # Already imported above with redirect

def get_theme_mode():
    settings_obj = StorefrontSettings.objects.first()
    if settings_obj:
        return settings_obj.theme_mode
    return 'auto'

def home(request):
    # Get featured mode from StorefrontSettings (admin only)
    mode = 'manual'
    settings_obj = StorefrontSettings.objects.first()
    if settings_obj:
        mode = settings_obj.featured_products_mode

    sort = request.GET.get('sort', 'featured')
    category_id = request.GET.get('category')
    subcategory_id = request.GET.get('subcategory')
    products_qs = Product.objects.all()
    if subcategory_id:
        products_qs = products_qs.filter(category_id=subcategory_id)
    elif category_id:
        # Show products in this category or any of its subcategories
        subcat_ids = list(Category.objects.filter(parent_id=category_id).values_list('id', flat=True))
        products_qs = products_qs.filter(category_id__in=[category_id] + subcat_ids)

    # Separate featured products
    featured_material = products_qs.filter(featured_manual=True, is_physical=True)
    featured_digital = products_qs.filter(featured_manual=True, is_digital=True)


    # Only show published products in the storefront
    products = products_qs.filter(draft=False)

    from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
    if sort == 'high_price':
        products = products.order_by('-price')
    elif sort == 'low_price':
        products = products.order_by('price')
    elif sort == 'most_viewed':
        products = products.order_by('-view_count')
    elif sort == 'most_purchased':
        products = products.order_by('-purchase_count')
    else:  # featured/manual
        if mode == 'most_viewed':
            products = products.order_by('-view_count')
        elif mode == 'most_purchased':
            products = products.order_by('-purchase_count')
        else:
            products = products.filter(featured_manual=True)

    paginator = Paginator(products, 12)  # 12 products per page
    page = request.GET.get('page')
    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)

    categories = Category.objects.all()
    material_categories = Category.objects.filter(product__is_physical=True).distinct()
    digital_categories = Category.objects.filter(product__is_digital=True).distinct()
    breadcrumb = []
    if category_id:
        cat = Category.objects.filter(id=category_id).first()
        if cat:
            breadcrumb.append({'name': cat.name, 'id': cat.pk, 'type': 'category'})
    if subcategory_id:
        subcat = Category.objects.filter(id=subcategory_id).first()
        if subcat:
            if subcat.parent:
                breadcrumb = [{'name': subcat.parent.name, 'id': subcat.parent.id, 'type': 'category'}]
            breadcrumb.append({'name': subcat.name, 'id': subcat.pk, 'type': 'subcategory'})
    unread_notifications_count = 0
    if request.user.is_authenticated:
        unread_notifications_count = request.user.notifications.filter(is_read=False).count()
    return render(request, 'storefront/home.html', {
        'products': products,
        'featured_mode': mode,
        'request': request,
        'categories': categories,
        'featured_material': featured_material,
        'featured_digital': featured_digital,
        'material_categories': material_categories,
        'digital_categories': digital_categories,
        'category_id': category_id,
        'subcategory_id': subcategory_id,
        'breadcrumb': breadcrumb,
        'unread_notifications_count': unread_notifications_count,
    })
