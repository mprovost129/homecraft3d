from django.contrib.auth.decorators import login_required
from django_ratelimit.decorators import ratelimit
from config.ratelimit_settings import LOGIN_RATELIMIT, REGISTER_RATELIMIT, PASSWORD_RESET_RATELIMIT
from accounts.permissions import owner_required
from django.shortcuts import render, redirect
from accounts.permissions import consumer_required
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.urls import reverse
from django.contrib.auth.views import PasswordResetView as DjangoPasswordResetView, PasswordResetDoneView as DjangoPasswordResetDoneView, PasswordResetConfirmView as DjangoPasswordResetConfirmView, PasswordResetCompleteView as DjangoPasswordResetCompleteView
from .forms import UserRegistrationForm, UserSettingsForm, UserLoginForm
from accounts.models import User, SellerProfile, ConsumerProfile
from .forms import UserProfileForm
from products.models import Product, Category
from orders.models import Order, LineItem
from reviews.models import Rating, Feedback
from storefront.models import StorefrontSettings
from django.db.models.functions import TruncMonth
from django.db.models import Count, Sum, F
from django.utils import timezone
from django.utils.decorators import method_decorator
import logging
security_logger = logging.getLogger('security')

@login_required
@owner_required
def owner_dashboard(request):
    if not request.user.is_owner:
        return render(request, '403.html', status=403)

    summary = {
        'user_count': User.objects.count(),
        'seller_count': SellerProfile.objects.count(),
        'consumer_count': ConsumerProfile.objects.count(),
        'product_count': Product.objects.count(),
        'order_count': Order.objects.count(),
        'review_count': Rating.objects.count(),
        'feedback_count': Feedback.objects.count(),
        'storefront_settings_count': StorefrontSettings.objects.count(),
    }
    latest_users = User.objects.order_by('-date_joined')[:5]
    latest_products = Product.objects.order_by('-id')[:5]
    latest_orders = Order.objects.order_by('-created_at')[:5]
    latest_reviews = Rating.objects.order_by('-created_at')[:5]

    # Dynamic sales data (total revenue per month)
    sales_qs = (
        LineItem.objects.annotate(month=TruncMonth('order__created_at'))
        .values('month')
        .annotate(total=Sum(F('quantity') * F('product__price')))
        .order_by('month')
    )
    sales_labels = [item['month'].strftime('%b %Y') for item in sales_qs]
    sales_data = [float(item['total']) if item['total'] else 0 for item in sales_qs]

    # Dynamic user growth data (new users per month)
    user_qs = (
        User.objects.annotate(month=TruncMonth('date_joined'))
        .values('month')
        .annotate(count=Count('id'))
        .order_by('month')
    )
    user_labels = [item['month'].strftime('%b %Y') for item in user_qs]
    user_data = [item['count'] for item in user_qs]

    material_categories = Category.objects.filter(product__is_physical=True).distinct()
    digital_categories = Category.objects.filter(product__is_digital=True).distinct()

    return render(request, 'accounts/owner_dashboard.html', {
        'user': request.user,
        'summary': summary,
        'latest_users': latest_users,
        'latest_products': latest_products,
        'latest_orders': latest_orders,
        'latest_reviews': latest_reviews,
        'sales_labels': sales_labels,
        'sales_data': sales_data,
        'user_labels': user_labels,
        'user_data': user_data,
        'material_categories': material_categories,
        'digital_categories': digital_categories,
    })

@consumer_required
def profile_view(request):
    if not request.user.is_authenticated:
        return redirect('accounts:login')
    user = request.user
    # All authenticated users can view their profile page
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            security_logger.info(f"Profile updated for user {user.username} (ID: {user.id}) from IP {request.META.get('REMOTE_ADDR')}")
            return render(request, 'accounts/profile.html', {'form': form, 'success': True})
    else:
        form = UserProfileForm(instance=user)
    return render(request, 'accounts/profile.html', {'form': form})

@ratelimit(key='ip', rate=LOGIN_RATELIMIT, method='POST', block=True)
def login_view(request):
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                if getattr(user, 'is_owner', False):
                    return redirect('accounts:owner_dashboard')
                elif getattr(user, 'is_seller', False):
                    return redirect('/sellers/dashboard/')
                else:
                    return redirect('accounts:profile')
            else:
                return render(request, 'accounts/login.html', {'form': form, 'error': 'Invalid credentials'})
        else:
            return render(request, 'accounts/login.html', {'form': form})
    else:
        form = UserLoginForm()
    return render(request, 'accounts/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('accounts:login')

@ratelimit(key='ip', rate=REGISTER_RATELIMIT, method='POST', block=True)
@ratelimit(key='ip', rate=REGISTER_RATELIMIT, method='POST', block=True)
def register_view(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  # Require email verification
            user.set_password(form.cleaned_data['password'])
            user.save()
            # Send verification email
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            verify_url = request.build_absolute_uri(
                reverse('accounts:verify_email', args=[uid, token])
            )
            subject = 'Verify your email - 3D Print Marketplace'
            message = render_to_string('accounts/email_verification.html', {
                'user': user,
                'verify_url': verify_url,
            })
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])
            security_logger.info(f"New registration for user {user.username} (ID: {user.id}) from IP {request.META.get('REMOTE_ADDR')}")
            return render(request, 'accounts/verification_sent.html')
        return render(request, 'accounts/register.html', {'form': form})
    else:
        form = UserRegistrationForm()
    return render(request, 'accounts/register.html', {'form': form})

def verify_email(request, uidb64, token):
    User = get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        return redirect('accounts:profile')
    return render(request, 'accounts/verification_failed.html')

@consumer_required
def settings_view(request):
    if not request.user.is_authenticated:
        return redirect('accounts:login')
    user = request.user
    if request.method == 'POST':
        form = UserSettingsForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            security_logger.info(f"Settings updated for user {user.username} (ID: {user.id}) from IP {request.META.get('REMOTE_ADDR')}")
            return render(request, 'accounts/settings.html', {'form': form, 'user': user, 'success': True})
    else:
        form = UserSettingsForm(instance=user)
    return render(request, 'accounts/settings.html', {'form': form, 'user': user})
