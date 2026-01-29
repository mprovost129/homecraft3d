from rest_framework import permissions

class IsSeller(permissions.BasePermission):
    def has_permission(self, request, view): # type: ignore
        return request.user.is_authenticated and getattr(request.user, 'is_seller', False)

class IsConsumer(permissions.BasePermission):
    def has_permission(self, request, view): # type: ignore
        return request.user.is_authenticated and getattr(request.user, 'is_consumer', False)

class IsOwner(permissions.BasePermission):
    def has_permission(self, request, view): # type: ignore
        return request.user.is_authenticated and getattr(request.user, 'is_owner', False)

# Decorators for function-based views
from functools import wraps
from django.http import HttpResponseForbidden

def seller_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated and getattr(request.user, 'is_seller', False):
            return view_func(request, *args, **kwargs)
        return HttpResponseForbidden('You must be a seller to access this page.')
    return _wrapped_view

def owner_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated and getattr(request.user, 'is_owner', False):
            return view_func(request, *args, **kwargs)
        return HttpResponseForbidden('You must be an owner/admin to access this page.')
    return _wrapped_view

def consumer_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated and getattr(request.user, 'is_consumer', False):
            return view_func(request, *args, **kwargs)
        return HttpResponseForbidden('You must be a consumer to access this page.')
    return _wrapped_view
