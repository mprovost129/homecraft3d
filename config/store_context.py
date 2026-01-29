def store_name(request):
    from django.conf import settings
    return {'STORE_NAME': getattr(settings, 'STORE_NAME', 'Home Craft 3d')}
