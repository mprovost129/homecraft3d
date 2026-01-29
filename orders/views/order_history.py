from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from orders.models import Order, LineItem

@login_required
def order_history_view(request):
    orders = Order.objects.filter(consumer=request.user).order_by('-created_at')
    return render(request, 'orders/order_history.html', {'orders': orders})
