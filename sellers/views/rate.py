from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Seller
from .models_rating import SellerRating
from .forms_rating import SellerRatingForm
from orders.models import Order

@login_required
def rate_seller(request, seller_id, order_id):
    seller = get_object_or_404(Seller, pk=seller_id)
    order = get_object_or_404(Order, pk=order_id, consumer=request.user)
    # Only allow rating if user purchased from this seller in this order
    if not order.lineitem_set.filter(product__seller=seller).exists():
        return redirect('order_history')
    # Only one rating per seller per order per user
    if SellerRating.objects.filter(seller=seller, user=request.user, order=order).exists():
        return redirect('order_history')
    if request.method == 'POST':
        form = SellerRatingForm(request.POST)
        if form.is_valid():
            rating = form.save(commit=False)
            rating.seller = seller
            rating.user = request.user
            rating.order = order
            rating.save()
            return redirect('order_history')
    else:
        form = SellerRatingForm()
    return render(request, 'sellers/rate_seller.html', {'form': form, 'seller': seller, 'order': order})
