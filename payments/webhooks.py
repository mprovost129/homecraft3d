
import stripe
import json
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.conf import settings
from sellers.models import Seller

@csrf_exempt
@require_POST
def stripe_webhook(request):
	payload = request.body
	sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
	endpoint_secret = getattr(settings, 'STRIPE_WEBHOOK_SECRET', None)
	event = None
	try:
		event = stripe.Webhook.construct_event(
			payload, sig_header, endpoint_secret
		)
	except ValueError as e:
		return HttpResponse(status=400)
	except stripe.error.SignatureVerificationError as e:
		return HttpResponse(status=400)

	# Handle the event
	if event['type'] == 'account.updated':
		account = event['data']['object']
		# Update seller Stripe status if needed
		try:
			seller = Seller.objects.get(stripe_account_id=account['id'])
			# Example: mark as payouts_enabled
			if account.get('payouts_enabled'):
				seller.stripe_payouts_enabled = True
				seller.save()
		except Seller.DoesNotExist:
			pass
	elif event['type'] == 'payment_intent.succeeded':
		# Handle successful payment (for Connect split logic)
		pass
	# Add more event types as needed

	return HttpResponse(status=200)
