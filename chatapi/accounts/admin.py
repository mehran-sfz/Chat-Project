from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Profile

class UserAdmin(BaseUserAdmin):
    # Define the fields to display in Django Admin
    list_display = ('phone_number', 'is_staff', 'is_superuser', 'is_active')
    search_fields = ('phone_number',)
    ordering = ('phone_number',)

    fieldsets = (
        (None, {'fields': ('phone_number', 'password')}),
        ('Permissions', {'fields': ('is_staff', 'is_active', 'is_superuser')}),
        ('Important dates', {'fields': ('last_login',)}),
        ('OTP Information', {'fields': ('otp', 'otp_expiry', 'otp_request_id')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('phone_number', 'password1', 'password2', 'is_staff', 'is_superuser'),
        }),
    )

admin.site.register(User, UserAdmin)

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'email', 'first_name', 'last_name', 'nationality_number', 'avatar', 'birth_date', 'created_at', 'updated_at')