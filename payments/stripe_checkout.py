from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
from django.conf import settings
from django.shortcuts import redirect
import stripe

from products.models import Product
from sellers.models import Seller

@csrf_exempt
def create_checkout_session(request):
    if request.method == 'POST':
        cart = request.session.get('cart', {})
        products = Product.objects.filter(id__in=cart.keys())
        if not products:
            return JsonResponse({'error': 'No products in cart.'}, status=400)

        # Assume all products in cart are from the same seller for now
        seller = products[0].seller
        stripe_account_id = seller.stripe_account_id
        if not stripe_account_id:
            return JsonResponse({'error': 'Seller is not connected to Stripe.'}, status=400)

        line_items = []
        total_amount = 0
        for product in products:
            quantity = cart[str(product.id)]
            price_cents = int(product.price * 100)
            total_amount += price_cents * quantity
            line_items.append({
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': product.name,
                    },
                    'unit_amount': price_cents,
                },
                'quantity': quantity,
            })

        # Platform fee: 10% (customize as needed)
        application_fee_amount = int(total_amount * 0.10)

        try:
            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=line_items,
                mode='payment',
                success_url=settings.BASE_DIR.as_posix() + '/payments/success/',
                cancel_url=settings.BASE_DIR.as_posix() + '/payments/cancel/',
                payment_intent_data={
                    'application_fee_amount': application_fee_amount,
                    'transfer_data': {
                        'destination': stripe_account_id,
                    },
                },
            )
            return JsonResponse({'id': session.id, 'url': session.url})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return HttpResponse(status=405)
