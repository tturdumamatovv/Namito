from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

# Register your models here.
from namito.catalog.admin import ReviewInline
from namito.orders.admin import OrderHistoryInline
from namito.users.models import User, UserAddress


class UserAdmin(BaseUserAdmin):
    list_display = ('phone_number', 'name', 'email', 'is_staff', 'date_of_birth', 'profile_picture')
    list_filter = ('is_staff', 'is_superuser',)
    fieldsets = (
        (None, {'fields': ('phone_number', 'password', 'profile_picture')}),
        ('Personal info', {'fields': ('name', 'full_name', 'date_of_birth', 'email')}),

    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('phone_number', 'name', 'email', 'password1', 'password2')}
         ),
    )
    search_fields = ('phone_number', 'name', 'email')
    ordering = ('phone_number',)
    filter_horizontal = ('groups', 'user_permissions',)
    inlines = [ReviewInline, OrderHistoryInline]


admin.site.register(User, UserAdmin)


@admin.register(UserAddress)
class UserAddressAdmin(admin.ModelAdmin):
    list_display = ('user', 'city', 'street', 'apartment_number', 'is_primary')
    list_filter = ('city', 'is_primary')
    search_fields = ('city', 'street', 'user__username', 'user__email')
    ordering = ('-created_at',)
