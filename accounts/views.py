# =================== IMPORTS ===================
import logging

from django import forms
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, get_user_model, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db.models import Count, F, Sum
from django.db.models.functions import TruncMonth
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.views.decorators.csrf import csrf_protect

from django_ratelimit.decorators import ratelimit

from accounts.models import ConsumerProfile, SellerProfile, User
from accounts.permissions import consumer_required, owner_required
from config.ratelimit_settings import LOGIN_RATELIMIT, PASSWORD_RESET_RATELIMIT, REGISTER_RATELIMIT
from orders.models import LineItem, Order
from products.models import Category, Product
from reviews.models import Feedback, Rating
from storefront.models import StorefrontSettings

from .forms import UserLoginForm, UserProfileForm, UserRegistrationForm, UserSettingsForm

# =================== LOGGING ===================
security_logger = logging.getLogger("security")


# =================== VIEWS ===================

def resend_verification_email(request):
    """
    Resend email verification link.

    IMPORTANT: This must be CSRF protected. A CSRF-exempt endpoint that triggers emails
    can be abused (even if rate-limited at login/register).
    """
    if request.method != "POST":
        return render(request, "accounts/resend_verification.html")

    email = (request.POST.get("email") or "").strip()
    if not email:
        return render(request, "accounts/resend_verification.html", {"error": "Please enter your email."})

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        # Avoid user enumeration? If you want to be strict, return a generic message.
        return render(request, "accounts/resend_verification.html", {"error": "No account found with that email."})

    if user.is_active:
        return render(
            request,
            "accounts/resend_verification.html",
            {"error": "Account is already active. Please log in."},
        )

    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    verify_url = request.build_absolute_uri(reverse("accounts:verify_email", args=[uid, token]))

    subject = "Verify your email - 3D Print Marketplace"
    message = render_to_string(
        "accounts/email_verification.html",
        {
            "user": user,
            "verify_url": verify_url,
        },
    )

    # If you're rendering HTML, pass html_message=... and a plain text fallback.
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])
    return render(request, "accounts/verification_sent.html", {"resent": True})


@login_required
@owner_required
def owner_dashboard(request):
    # owner_required should already enforce this, so this check is redundant.
    if not request.user.is_owner:
        return render(request, "403.html", status=403)

    summary = {
        "user_count": User.objects.count(),
        "seller_count": SellerProfile.objects.count(),
        "consumer_count": ConsumerProfile.objects.count(),
        "product_count": Product.objects.count(),
        "order_count": Order.objects.count(),
        "review_count": Rating.objects.count(),
        "feedback_count": Feedback.objects.count(),
        "storefront_settings_count": StorefrontSettings.objects.count(),
    }
    latest_users = User.objects.order_by("-date_joined")[:5]
    latest_products = Product.objects.order_by("-id")[:5]
    latest_orders = Order.objects.order_by("-created_at")[:5]
    latest_reviews = Rating.objects.order_by("-created_at")[:5]

    # Dynamic sales data (total revenue per month)
    sales_qs = (
        LineItem.objects.annotate(month=TruncMonth("order__created_at"))
        .values("month")
        .annotate(total=Sum(F("quantity") * F("product__price")))
        .order_by("month")
    )
    sales_labels = [item["month"].strftime("%b %Y") for item in sales_qs if item["month"]]
    sales_data = [float(item["total"]) if item["total"] else 0 for item in sales_qs]

    # Dynamic user growth data (new users per month)
    user_qs = (
        User.objects.annotate(month=TruncMonth("date_joined"))
        .values("month")
        .annotate(count=Count("id"))
        .order_by("month")
    )
    user_labels = [item["month"].strftime("%b %Y") for item in user_qs if item["month"]]
    user_data = [item["count"] for item in user_qs]

    # NOTE: This currently only shows categories that have at least one product of the given type.
    # If you want full category trees, build them separately and prefetch.
    material_categories = Category.objects.filter(product__is_physical=True).distinct()
    digital_categories = Category.objects.filter(product__is_digital=True).distinct()

    return render(
        request,
        "accounts/owner_dashboard.html",
        {
            "user": request.user,
            "summary": summary,
            "latest_users": latest_users,
            "latest_products": latest_products,
            "latest_orders": latest_orders,
            "latest_reviews": latest_reviews,
            "sales_labels": sales_labels,
            "sales_data": sales_data,
            "user_labels": user_labels,
            "user_data": user_data,
            "material_categories": material_categories,
            "digital_categories": digital_categories,
        },
    )


@consumer_required
def profile_view(request):
    if not request.user.is_authenticated:
        return redirect("accounts:login")

    user = request.user

    if request.method == "POST":
        form = UserProfileForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            security_logger.info(
                "Profile updated for user %s (ID: %s) from IP %s",
                user.username,
                user.id,
                request.META.get("REMOTE_ADDR"),
            )
            return render(request, "accounts/profile.html", {"form": form, "success": True})
    else:
        form = UserProfileForm(instance=user)

    return render(request, "accounts/profile.html", {"form": form})


# =================== LOGIN/LOGOUT/REGISTER VIEWS ===================

@ratelimit(key="ip", rate=LOGIN_RATELIMIT, method="POST", block=True)
def login_view(request):
    if request.method == "POST":
        form = UserLoginForm(request.POST)
        if not form.is_valid():
            return render(request, "accounts/login.html", {"form": form})

        username = form.cleaned_data["username"]
        password = form.cleaned_data["password"]
        user = authenticate(request, username=username, password=password)

        if user is not None:
            if not user.is_active:
                # If you require email verification, this is helpful UX.
                return render(
                    request,
                    "accounts/login.html",
                    {"form": form, "error": "Please verify your email before logging in."},
                )

            login(request, user)

            if getattr(user, "is_owner", False):
                return redirect("accounts:owner_dashboard")
            if getattr(user, "is_seller", False):
                return redirect("/sellers/dashboard/")
            return redirect("accounts:profile")

        return render(request, "accounts/login.html", {"form": form, "error": "Invalid credentials"})

    form = UserLoginForm()
    return render(request, "accounts/login.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect("accounts:login")


@csrf_protect
@ratelimit(key="ip", rate=REGISTER_RATELIMIT, method="POST", block=True)
def register_view(request):
    error_message = None

    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)

            # If your UserRegistrationForm already sets password (common pattern),
            # do not set it again. Keeping your current behavior but note:
            # - Calling set_password with form.cleaned_data['password'] assumes that field exists
            #   and is validated.
            user.is_active = False  # Require email verification
            user.set_password(form.cleaned_data["password"])
            user.save()

            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            verify_url = request.build_absolute_uri(reverse("accounts:verify_email", args=[uid, token]))

            subject = "Verify your email - 3D Print Marketplace"
            message = render_to_string(
                "accounts/email_verification.html",
                {
                    "user": user,
                    "verify_url": verify_url,
                },
            )
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])

            security_logger.info(
                "New registration for user %s (ID: %s) from IP %s",
                user.username,
                user.id,
                request.META.get("REMOTE_ADDR"),
            )
            return render(request, "accounts/verification_sent.html")

        error_message = "Please correct the errors below."
    else:
        form = UserRegistrationForm()

    return render(request, "accounts/register.html", {"form": form, "error_message": error_message})


def verify_email(request, uidb64, token):
    UserModel = get_user_model()

    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = UserModel.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, UserModel.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        return redirect("accounts:profile")

    return render(request, "accounts/verification_failed.html")


@consumer_required
def settings_view(request):
    if not request.user.is_authenticated:
        return redirect("accounts:login")

    user = request.user

    if request.method == "POST":
        form = UserSettingsForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            security_logger.info(
                "Settings updated for user %s (ID: %s) from IP %s",
                user.username,
                user.id,
                request.META.get("REMOTE_ADDR"),
            )
            return render(request, "accounts/settings.html", {"form": form, "user": user, "success": True})
    else:
        form = UserSettingsForm(instance=user)

    return render(request, "accounts/settings.html", {"form": form, "user": user})


# =================== BECOME SELLER VIEW ===================

class BecomeSellerForm(forms.Form):
    agree_terms = forms.BooleanField(required=True, label="I agree to the seller terms")


@consumer_required
def become_seller_view(request):
    user = request.user

    # NOTE: Your models file uses related_name="seller_profile".
    # If you didn't apply that change in your actual project yet, this should be:
    # hasattr(user, 'sellerprofile')
    if hasattr(user, "seller_profile") or hasattr(user, "sellerprofile"):
        messages.info(request, "You are already a seller.")
        return redirect("accounts:profile")

    if request.method == "POST":
        form = BecomeSellerForm(request.POST)
        if form.is_valid():
            # Create SellerProfile for individual
            SellerProfile.objects.create(user=user, display_name=user.username)
            user.is_seller = True
            user.save()

            stripe_signup_url = reverse("payments:stripe_onboard")
            messages.success(request, "You are now a seller! Please complete your Stripe onboarding.")
            return redirect(stripe_signup_url)
    else:
        form = BecomeSellerForm()

    return render(request, "accounts/become_seller.html", {"form": form})
