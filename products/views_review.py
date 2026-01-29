from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Product
from .models_review import ProductReview
from .forms_review import ProductReviewForm

from django.contrib import messages
from django.core.mail import send_mail
from django.urls import reverse
from django.conf import settings
from accounts.models import User
from accounts.models_notification import Notification

@login_required
def add_review(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    try:
        review = ProductReview.objects.get(product=product, user=request.user)
    except ProductReview.DoesNotExist:
        review = None
    if request.method == 'POST':
        form = ProductReviewForm(request.POST, instance=review)
        if form.is_valid():
            review = form.save(commit=False)
            review.product = product
            review.user = request.user
            review.save()
            # Notify seller if review is for their product
            seller_user = getattr(product.seller, 'user', None)
            review_url = request.build_absolute_uri(reverse('product_detail', args=[product.id]))
            notif_message = f"Your product '{product.name}' received a new review."
            if seller_user and seller_user != request.user:
                # In-app notification
                if getattr(seller_user, 'notify_reviews_inapp', True):
                    Notification.objects.create(
                        user=seller_user,
                        message=notif_message,
                        url=review_url
                    )
                # Email notification
                if getattr(seller_user, 'notify_reviews_email', True) and seller_user.email:
                    subject = f"New review for your product: {product.name}"
                    message = (
                        f"Hello {seller_user.username},\n\n"
                        f"Your product '{product.name}' has received a new review.\n\n"
                        f"Title: {review.title}\n"
                        f"Rating: {review.rating}\n"
                        f"Review: {review.body}\n\n"
                        f"View the review: {review_url}\n\n"
                        f"- The 3D Print Marketplace Team"
                    )
                    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [seller_user.email], fail_silently=True)
            messages.success(request, 'Your review has been submitted.')
            return redirect('product_detail', product_id=product.id)
    else:
        form = ProductReviewForm(instance=review)
    return render(request, 'products/add_review.html', {'form': form, 'product': product, 'review': review})
