import stripe
from django.conf import settings
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from accounts.models import SellerProfile

stripe.api_key = settings.STRIPE_SECRET_KEY

@login_required
def stripe_onboard(request):
    user = request.user
    try:
        seller_profile = user.sellerprofile
    except SellerProfile.DoesNotExist:
        return redirect('accounts:become_seller')

    # If already connected, skip onboarding
    if seller_profile.stripe_account_id:
        return redirect('/sellers/dashboard/')

    # Create a Stripe account if not exists
    if not seller_profile.stripe_account_id:
        account = stripe.Account.create(
            type='express',
            country='US',
            email=user.email,
            business_type='individual',
            capabilities={
                'transfers': {'requested': True},
            },
        )
        seller_profile.stripe_account_id = account.id
        seller_profile.save()
    else:
        account = stripe.Account.retrieve(seller_profile.stripe_account_id)

    # Create an onboarding link
    account_link = stripe.AccountLink.create(
        account=account.id,
        refresh_url=request.build_absolute_uri('/payments/stripe/onboard/'),
        return_url=request.build_absolute_uri('/sellers/dashboard/'),
        type='account_onboarding',
    )
    return redirect(account_link.url)
