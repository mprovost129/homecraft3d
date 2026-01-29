# Wishlist views

from django.contrib.auth.decorators import login_required, user_passes_test
from accounts.permissions import owner_required
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models_wishlist import Wishlist
from .models import Product, Category
from .forms import CategoryForm
from accounts.models import User
from accounts.models_notification import Notification
from django.core.mail import send_mail
from django.conf import settings

# Helper for admin check
def is_owner(user):
    return getattr(user, 'is_owner', False)

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

from django.shortcuts import render, get_object_or_404
from .models import Product
from django.contrib import messages

def product_list(request):
    # Search and filtering
    from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
    products = Product.objects.filter(draft=False)
    categories = Category.objects.all()
    sellers = User.objects.filter(is_seller=True)
    query = request.GET.get('q', '').strip()
    category_id = request.GET.get('category', '')
    price_min = request.GET.get('price_min', '')
    price_max = request.GET.get('price_max', '')
    tags = request.GET.get('tags', '').strip()
    seller_id = request.GET.get('seller', '')
    min_rating = request.GET.get('min_rating', '')
    sort = request.GET.get('sort', 'newest')
    page = request.GET.get('page', 1)
    per_page = 9

    if query:
        products = products.filter(name__icontains=query)
    if tags:
        for tag in tags.split(','):
            tag = tag.strip()
            if tag:
                products = products.filter(tags__icontains=tag)
    if seller_id:
        products = products.filter(seller__user__id=seller_id)
        # Build nested category list for dropdown
        def get_category_tree(categories, parent=None, level=0):
            tree = []
            for cat in categories.filter(parent=parent).order_by('position', 'name'):
                tree.append({'id': cat.id, 'name': cat.name, 'level': level})
                tree += get_category_tree(categories, parent=cat, level=level+1)
            return tree

        all_categories = Category.objects.all()
        category_tree = get_category_tree(all_categories)
        products = products.filter(category_id=category_id)
    if price_min:
        try:
            products = products.filter(price__gte=float(price_min))
        except ValueError:
            pass
    if price_max:
        try:
            products = products.filter(price__lte=float(price_max))
        except ValueError:
            pass

    # Sorting
    if sort == 'price_asc':
        products = products.order_by('price')
    elif sort == 'price_desc':
        products = products.order_by('-price')
    elif sort == 'name':
        products = products.order_by('name')
    else:  # newest
        products = products.order_by('-id')

    # Filter by min_rating (aggregate)
    from .models_review import ProductReview
    from django.db.models import Avg
    if min_rating:
        try:
            min_rating_val = float(min_rating)
            product_ids = [p.pk for p in products]
            ratings = ProductReview.objects.filter(product_id__in=product_ids).values('product').annotate(avg=Avg('rating'))
            ids = [r['product'] for r in ratings if r['avg'] and r['avg'] >= min_rating_val]
            products = products.filter(id__in=ids)
        except Exception:
            pass

    paginator = Paginator(products, per_page)
    try:
        products_page = paginator.page(page)
    except PageNotAnInteger:
        products_page = paginator.page(1)
    except EmptyPage:
        products_page = paginator.page(paginator.num_pages)

    # Wishlist product IDs for current user
    wishlist_product_ids = set()
    if request.user.is_authenticated:
        wishlist, _ = Wishlist.objects.get_or_create(user=request.user)
        wishlist_product_ids = set(wishlist.products.values_list('id', flat=True))

    # Average ratings for products on this page
    from .models_review import ProductReview
    from django.db.models import Avg
    avg_ratings = {}
    for prod in products_page:
        avg = ProductReview.objects.filter(product=prod).aggregate(Avg('rating'))['rating__avg']
        avg_ratings[prod.id] = avg

    return render(request, 'products/product_list.html', {
        'products': products_page,
        'categories': categories,
        'sellers': sellers,
        'query': query,
        'category_id': category_id,
        'price_min': price_min,
        'price_max': price_max,
        'tags': tags,
        'seller_id': seller_id,
        'min_rating': min_rating,
        'sort': sort,
        'paginator': paginator,
        'page_obj': products_page,
        'is_paginated': paginator.num_pages > 1,
        'wishlist_product_ids': wishlist_product_ids,
        'avg_ratings': avg_ratings,
    })

@owner_required
def category_list(request):
    categories = Category.objects.all()
    form = CategoryForm()
    return render(request, 'products/category_list.html', {'categories': categories, 'form': form})

@owner_required
def category_add(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES)
        if form.is_valid():
            new_cat = form.save()
            # Notify all admins (owners) with admin notifications enabled
            for admin in User.objects.filter(is_owner=True):
                notif_message = f"Category '{new_cat.name}' was added."
                if getattr(admin, 'notify_admin_inapp', True):
                    Notification.objects.create(
                        user=admin,
                        message=notif_message,
                        url=''  # Optionally link to category list
                    )
                if getattr(admin, 'notify_admin_email', True) and admin.email:
                    subject = "Category Added"
                    message = (
                        f"Hello {admin.username},\n\nCategory '{new_cat.name}' was added.\n\n- The 3D Print Marketplace Team"
                    )
                    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [admin.email], fail_silently=True)
            return redirect('category_list')
    return redirect('category_list')

@owner_required
def category_delete(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    cat_name = category.name
    category.delete()
    for admin in User.objects.filter(is_owner=True):
        notif_message = f"Category '{cat_name}' was deleted."
        if getattr(admin, 'notify_admin_inapp', True):
            Notification.objects.create(
                user=admin,
                message=notif_message,
                url=''
            )
        if getattr(admin, 'notify_admin_email', True) and admin.email:
            subject = "Category Deleted"
            message = (
                f"Hello {admin.username},\n\nCategory '{cat_name}' was deleted.\n\n- The 3D Print Marketplace Team"
            )
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [admin.email], fail_silently=True)
    return redirect('category_list')

@owner_required
def category_edit(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category updated successfully.')
            for admin in User.objects.filter(is_owner=True):
                notif_message = f"Category '{category.name}' was updated."
                if getattr(admin, 'notify_admin_inapp', True):
                    Notification.objects.create(
                        user=admin,
                        message=notif_message,
                        url=''
                    )
                if getattr(admin, 'notify_admin_email', True) and admin.email:
                    subject = "Category Edited"
                    message = (
                        f"Hello {admin.username},\n\nCategory '{category.name}' was updated.\n\n- The 3D Print Marketplace Team"
                    )
                    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [admin.email], fail_silently=True)
        else:
            messages.error(request, 'Please correct the errors below.')
    return redirect('category_list')

@owner_required
def category_reorder(request, category_id, direction):
    category = get_object_or_404(Category, id=category_id)
    moved = False
    if direction == 'up':
        prev = Category.objects.filter(position__lt=category.position).order_by('-position').first()
        if prev:
            category.position, prev.position = prev.position, category.position
            category.save()
            prev.save()
            moved = True
    elif direction == 'down':
        next = Category.objects.filter(position__gt=category.position).order_by('position').first()
        if next:
            category.position, next.position = next.position, category.position
            category.save()
            next.save()
            moved = True
    if moved:
        for admin in User.objects.filter(is_owner=True):
            notif_message = f"Category '{category.name}' was reordered."
            if getattr(admin, 'notify_admin_inapp', True):
                Notification.objects.create(
                    user=admin,
                    message=notif_message,
                    url=''
                )
            if getattr(admin, 'notify_admin_email', True) and admin.email:
                subject = "Category Reordered"
                message = (
                    f"Hello {admin.username},\n\nCategory '{category.name}' was reordered.\n\n- The 3D Print Marketplace Team"
                )
                send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [admin.email], fail_silently=True)
    return redirect('category_list')

# Product detail view
def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    from .models_review import ProductReview
    from django.db import models as djmodels
    reviews = ProductReview.objects.filter(product=product).select_related('user').all()
    avg_rating = reviews.aggregate(djmodels.Avg('rating'))['rating__avg']
    user_review = None
    if request.user.is_authenticated:
        user_review = reviews.filter(user=request.user).first()

    # Related products: use StorefrontSettings to determine filter mode
    from storefront.models import StorefrontSettings
    mode = 'most_purchased'
    settings_obj = StorefrontSettings.objects.first()
    if settings_obj:
        mode = settings_obj.featured_products_mode
    related_qs = Product.objects.filter(category=product.category).exclude(pk=product.pk)
    if mode == 'most_viewed':
        related_products = related_qs.order_by('-view_count')[:4]
    elif mode == 'manual':
        related_products = related_qs.filter(featured_manual=True)[:4]
    else:  # most_purchased (default)
        related_products = related_qs.order_by('-purchase_count', '-view_count')[:4]

    return render(request, 'products/product_detail.html', {
        'product': product,
        'reviews': reviews,
        'avg_rating': avg_rating,
        'user_review': user_review,
        'related_products': related_products,
    })
