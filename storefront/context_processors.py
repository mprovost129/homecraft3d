from .models import StorefrontSettings
def theme_mode(request):
    user_mode = None
    if request.user.is_authenticated:
        user_mode = getattr(request.user, 'theme_preference', None)
        if user_mode:
            return {'theme_mode': user_mode}
    settings_obj = StorefrontSettings.objects.first()
    return {'theme_mode': settings_obj.theme_mode if settings_obj else 'auto'}
from django.conf import settings

def cart_item_count(request):
    cart = request.session.get('cart', {})
    count = sum(item.get('quantity', 1) for item in cart.values())
    return {'cart_item_count': count}
