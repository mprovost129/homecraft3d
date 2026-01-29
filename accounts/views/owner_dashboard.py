from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def owner_dashboard(request):
    if not request.user.is_owner:
        return render(request, '403.html', status=403)
    return render(request, 'accounts/owner_dashboard.html', {'user': request.user})
