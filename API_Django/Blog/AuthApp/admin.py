from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Profile

class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile'
    fk_name = 'user'
    readonly_fields = ('created_at',)

class CustomUserAdmin(BaseUserAdmin):
    inlines = (ProfileInline,)
    list_display = (
        'username', 'email', 'is_superuser', 'is_staff', 'is_active',
        'date_joined', 'get_profile_created_at', 'get_categories_display'
    )
    list_filter = ('is_superuser', 'is_staff', 'is_active')

    def get_profile_created_at(self, obj):
        if hasattr(obj, 'auth_profile'):
            return obj.auth_profile.created_at
        return '-'
    get_profile_created_at.short_description = 'Profile Created At'

    def get_categories_display(self, obj):
        if hasattr(obj, 'auth_profile'):
            return obj.auth_profile.get_categories_display()
        return '-'
    get_categories_display.short_description = 'Categories'

# Unregister the default User admin and register the customized one
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
