from django.shortcuts import render

def moderation_dashboard(request):
    return render(request, 'moderation/dashboard.html')
