from django.shortcuts import render, get_object_or_404
from ..models import Seller

def seller_profile(request, seller_id):
    seller = get_object_or_404(Seller, pk=seller_id)
    return render(request, 'sellers/profile.html', {'seller': seller})
