from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, SellerProfile, ConsumerProfile

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    def get_model_perms(self, request):
        # Only show in admin index if user is staff or superuser
        perms = super().get_model_perms(request)
        return perms
    User._meta.verbose_name = 'Staff'
    User._meta.verbose_name_plural = 'Staff'
    fieldsets = list(BaseUserAdmin.fieldsets) + [
        (None, {'fields': ('is_seller', 'is_consumer', 'is_owner')}),
    ]
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        (None, {'fields': ('is_seller', 'is_consumer', 'is_owner')}),
    )
    list_display = tuple(BaseUserAdmin.list_display) + ('is_seller', 'is_consumer', 'is_owner')
    list_filter = tuple(BaseUserAdmin.list_filter) + ('is_seller', 'is_consumer', 'is_owner')


@admin.register(SellerProfile)
class SellerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'display_name')
    search_fields = ('user__username', 'display_name')


@admin.register(ConsumerProfile)
class ConsumerProfileAdmin(admin.ModelAdmin):
    list_display = ('user',)
    search_fields = ('user__username',)
