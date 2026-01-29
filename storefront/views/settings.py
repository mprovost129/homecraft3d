from django.contrib.auth.decorators import user_passes_test, login_required
from django.shortcuts import render, redirect
from .models import StorefrontSettings
from .forms import StorefrontSettingsForm

def is_owner_or_admin(user):
    return user.is_authenticated and (user.is_superuser or getattr(user, 'is_owner', False))

@login_required
@user_passes_test(is_owner_or_admin)
def storefront_settings_view(request):
    settings_obj, _ = StorefrontSettings.objects.get_or_create(pk=1)
    if request.method == 'POST':
        form = StorefrontSettingsForm(request.POST, instance=settings_obj)
        if form.is_valid():
            form.save()
            return redirect('storefront_settings')
    else:
        form = StorefrontSettingsForm(instance=settings_obj)
    return render(request, 'storefront/storefront_settings.html', {'form': form})
