
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, SellerProfile, ConsumerProfile




# Main User admin: shows all users
@admin.register(User)
class UserAdmin(BaseUserAdmin):
    def get_model_perms(self, request):
        # Show in admin index for everyone
        return super().get_model_perms(request)
    User._meta.verbose_name = 'User'
    User._meta.verbose_name_plural = 'Users'
    fieldsets = list(BaseUserAdmin.fieldsets) + [
        (None, {'fields': ('is_seller', 'is_consumer', 'is_owner')}),
    ]
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        (None, {'fields': ('is_seller', 'is_consumer', 'is_owner')}),
    )
    list_display = tuple(BaseUserAdmin.list_display) + ('is_seller', 'is_consumer', 'is_owner')
    list_filter = tuple(BaseUserAdmin.list_filter) + ('is_seller', 'is_consumer', 'is_owner')

    actions = ['verify_selected_users']

    def get_queryset(self, request):
        return super().get_queryset(request)

    def verify_selected_users(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f"{updated} user(s) manually verified.")
    verify_selected_users.short_description = "Manually verify selected users (activate account)"




@admin.register(SellerProfile)
class SellerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'display_name')
    search_fields = ('user__username', 'display_name')


@admin.register(ConsumerProfile)
class ConsumerProfileAdmin(admin.ModelAdmin):
    list_display = ('user',)
    search_fields = ('user__username',)
