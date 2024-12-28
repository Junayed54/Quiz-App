from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User

class UserAdmin(BaseUserAdmin):
    # Fields to display in the admin interface
    list_display = ('email', 'is_staff', 'is_superuser', 'is_active')
    list_filter = ('is_staff', 'is_superuser', 'is_active')
    
    # Fieldsets for organizing the form in the admin interface
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Permissions'), {'fields': ('is_staff', 'is_superuser', 'is_active')}),
        (_('Important dates'), {'fields': ('last_login',)}),
    )
    
    # Fields for creating a new user in the admin interface
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'is_staff', 'is_superuser', 'is_active'),
        }),
    )
    
    # Configurations for searching and ordering
    search_fields = ('email',)
    ordering = ('email',)
    filter_horizontal = ()

# Register the User model with the custom admin
admin.site.register(User, UserAdmin)
