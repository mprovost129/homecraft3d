from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from products.models import Product

@login_required
def seller_product_analytics(request):
    if not hasattr(request.user, 'seller'):
        return redirect('/')
    seller = request.user.seller
    products = Product.objects.filter(seller=seller)
    analytics = []
    for product in products:
        views = product.view_count
        purchases = product.purchase_count
        conversion_rate = (purchases / views * 100) if views else 0
        analytics.append({
            'product': product,
            'views': views,
            'purchases': purchases,
            'conversion_rate': conversion_rate,
        })
    return render(request, 'sellers/product_analytics.html', {'analytics': analytics})
from django.contrib.auth.decorators import login_required
from accounts.permissions import seller_required
from django.shortcuts import get_object_or_404, redirect, render
from products.models import Product, Media
from products.forms import ProductForm, MediaForm, ProductVariantFormSet
@login_required
@seller_required
def remove_media(request, product_id, media_id):
    if not hasattr(request.user, 'seller'):
        return redirect('/')
    seller = request.user.seller
    product = get_object_or_404(Product, id=product_id, seller=seller)
    media = get_object_or_404(Media, id=media_id)
    if request.method == 'POST':
        product.media.remove(media)
        media.delete()
        return redirect('edit_product', product_id=product.pk)
    return redirect('edit_product', product_id=product.pk)
from django.shortcuts import get_object_or_404
@login_required
@seller_required
def edit_product(request, product_id):
    if not hasattr(request.user, 'seller'):
        return redirect('/')
    seller = request.user.seller
    product = get_object_or_404(Product, id=product_id, seller=seller)
    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        media_form = MediaForm(request.POST, request.FILES)
        variant_formset = ProductVariantFormSet(request.POST, instance=product)
        if form.is_valid() and media_form.is_valid() and variant_formset.is_valid():
            product = form.save(commit=False)
            product.draft = form.cleaned_data.get('draft', False)
            product.is_digital = form.cleaned_data.get('is_digital', False)
            product.is_physical = form.cleaned_data.get('is_physical', False)
            product.length_mm = form.cleaned_data.get('length_mm')
            product.width_mm = form.cleaned_data.get('width_mm')
            product.height_mm = form.cleaned_data.get('height_mm')
            product.inventory = form.cleaned_data.get('inventory')
            product.meta_title = form.cleaned_data.get('meta_title')
            product.meta_description = form.cleaned_data.get('meta_description')
            product.save()
            # Add new media if present (multiple files/images)
            files = request.FILES.getlist('file')
            images = request.FILES.getlist('image')
            file_type = media_form.cleaned_data.get('file_type')
            for file in files:
                media = Media.objects.create(file=file, file_type=file_type)
                product.media.add(media)
            for image in images:
                media = Media.objects.create(image=image, file_type=file_type)
                product.media.add(media)
            variant_formset.save()
            return redirect('manage_products')
    else:
        form = ProductForm(instance=product)
        media_form = MediaForm()
        variant_formset = ProductVariantFormSet(instance=product)
    return render(request, 'sellers/edit_product.html', {
        'form': form,
        'media_form': media_form,
        'variant_formset': variant_formset,
        'product': product,
    })

@login_required
@seller_required
def delete_product(request, product_id):
    if not hasattr(request.user, 'seller'):
        return redirect('/')
    seller = request.user.seller
    product = get_object_or_404(Product, id=product_id, seller=seller)
    if request.method == 'POST':
        product.delete()
        return redirect('manage_products')
    return render(request, 'sellers/delete_product.html', {'product': product})

from django.db import transaction

@login_required
@seller_required
def duplicate_product(request, product_id):
    if not hasattr(request.user, 'seller'):
        return redirect('/')
    seller = request.user.seller
    product = get_object_or_404(Product, id=product_id, seller=seller)
    with transaction.atomic():
        # Duplicate product fields
        new_product = Product.objects.create(
            name=product.name + " (Copy)",
            description=product.description,
            seller=seller,
            price=product.price,
            category=product.category,
            license=product.license,
            is_digital=product.is_digital,
            is_physical=product.is_physical,
            length_mm=product.length_mm,
            width_mm=product.width_mm,
            height_mm=product.height_mm,
            featured_manual=False,
        )
        # Duplicate media
        for media in product.media.all():
            # Only link existing media, do not copy files
            new_product.media.add(media)
    from django.contrib import messages
    messages.success(request, f"Product '{product.name}' duplicated.")
    return redirect('manage_products')

@login_required
@seller_required
def manage_products(request):
    if not hasattr(request.user, 'seller'):
        return redirect('/')
    seller = request.user.seller
    if request.method == 'POST':
        # Bulk actions
        action = request.POST.get('bulk_action')
        selected_ids = request.POST.getlist('selected_products')
        if action and selected_ids:
            products_qs = Product.objects.filter(seller=seller, id__in=selected_ids)
            if action == 'delete':
                products_qs.delete()
                from django.contrib import messages
                messages.success(request, f"Deleted {len(selected_ids)} products.")
            elif action == 'feature':
                products_qs.update(featured_manual=True)
                from django.contrib import messages
                messages.success(request, f"Featured {len(selected_ids)} products.")
            elif action == 'unfeature':
                products_qs.update(featured_manual=False)
                from django.contrib import messages
                messages.success(request, f"Unfeatured {len(selected_ids)} products.")
            return redirect('manage_products')
        # Single product upload
        form = ProductForm(request.POST)
        media_form = MediaForm(request.POST, request.FILES)
        if form.is_valid() and media_form.is_valid():
            product = form.save(commit=False)
            product.seller = seller
            product.is_digital = form.cleaned_data.get('is_digital', False)
            product.is_physical = form.cleaned_data.get('is_physical', False)
            product.length_mm = form.cleaned_data.get('length_mm')
            product.width_mm = form.cleaned_data.get('width_mm')
            product.height_mm = form.cleaned_data.get('height_mm')
            product.draft = form.cleaned_data.get('draft', False)
            product.inventory = form.cleaned_data.get('inventory')
            product.meta_title = form.cleaned_data.get('meta_title')
            product.meta_description = form.cleaned_data.get('meta_description')
            product.save()
            files = request.FILES.getlist('file')
            images = request.FILES.getlist('image')
            file_type = media_form.cleaned_data.get('file_type')
            for file in files:
                media = Media.objects.create(file=file, file_type=file_type)
                product.media.add(media)
            for image in images:
                media = Media.objects.create(image=image, file_type=file_type)
                product.media.add(media)
            return redirect('manage_products')
    else:
        form = ProductForm()
        media_form = MediaForm()
    products = Product.objects.filter(seller=seller)
    return render(request, 'sellers/manage_products.html', {
        'form': form,
        'media_form': media_form,
        'products': products,
    })
