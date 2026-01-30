from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models_collection import Collection
from products.models import Product
from accounts.models import User
from django.http import HttpResponseForbidden

@login_required
def collection_list(request):
    collections = Collection.objects.filter(owner=request.user)
    return render(request, 'products/collection_list.html', {'collections': collections})

@login_required
def collection_create(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description', '')
        is_public = bool(request.POST.get('is_public'))
        collection = Collection.objects.create(name=name, description=description, owner=request.user, is_public=is_public)
        return redirect('collection_list')
    return render(request, 'products/collection_create.html')

@login_required
def collection_add_product(request, collection_id, product_id):
    collection = get_object_or_404(Collection, id=collection_id, owner=request.user)
    product = get_object_or_404(Product, id=product_id)
    collection.products.add(product)
    return redirect('collection_detail', collection_id=collection.pk)

@login_required
def collection_remove_product(request, collection_id, product_id):
    collection = get_object_or_404(Collection, id=collection_id, owner=request.user)
    product = get_object_or_404(Product, id=product_id)
    collection.products.remove(product)
    return redirect('collection_detail', collection_id=collection.pk)

@login_required
def collection_detail(request, collection_id):
    collection = get_object_or_404(Collection, id=collection_id, owner=request.user)
    return render(request, 'products/collection_detail.html', {'collection': collection})

def collection_share(request, share_uuid):
    collection = get_object_or_404(Collection, share_uuid=share_uuid, is_public=True)
    return render(request, 'products/collection_share.html', {'collection': collection})
