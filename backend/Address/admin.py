from django.contrib import admin
from .models import Address


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('user', 'full_name', 'city', 'state', 'is_default', 'created_at')
    list_filter = ('address_type', 'is_default', 'country', 'created_at')
    search_fields = ('user__username', 'full_name', 'city', 'state', 'postal_code')
    readonly_fields = ('created_at', 'updated_at')
