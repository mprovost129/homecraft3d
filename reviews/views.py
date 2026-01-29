from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Rating
from .forms import RatingForm
from products.models import Product

def review_list(request):
    reviews = Rating.objects.select_related('product', 'user').order_by('-created_at')
    return render(request, 'reviews/review_list.html', {'reviews': reviews})

@login_required
def review_create(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    if Rating.objects.filter(product=product, user=request.user).exists():
        return redirect('product_detail', product_id=product.pk)
    if request.method == 'POST':
        form = RatingForm(request.POST)
        if form.is_valid():
            rating = form.save(commit=False)
            rating.product = product
            rating.user = request.user
            rating.save()
            return redirect('product_detail', product_id=product.pk)
    else:
        form = RatingForm()
    return render(request, 'reviews/review_form.html', {'form': form, 'product': product})

@login_required
def review_edit(request, review_id):
    review = get_object_or_404(Rating, pk=review_id, user=request.user)
    if request.method == 'POST':
        form = RatingForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            return redirect('product_detail', product_id=review.product.id)
    else:
        form = RatingForm(instance=review)
    return render(request, 'reviews/review_form.html', {'form': form, 'product': review.product, 'edit': True})

@login_required
def review_delete(request, review_id):
    review = get_object_or_404(Rating, pk=review_id, user=request.user)
    product_id = review.product.id
    if request.method == 'POST':
        review.delete()
        return redirect('product_detail', product_id=product_id)
    return render(request, 'reviews/review_confirm_delete.html', {'review': review})
