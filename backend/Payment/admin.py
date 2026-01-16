from django.contrib import admin
from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer_name', 'order', 'amount', 'paid_via', 'status', 'payment_date')
    list_filter = ('status', 'paid_via', 'payment_date', 'created_at')
    search_fields = ('customer_name', 'customer__username', 'transaction_id', 'order__id')
    readonly_fields = ('created_at', 'updated_at', 'payment_date')
    date_hierarchy = 'payment_date'
    
    fieldsets = (
        ('Payment Information', {
            'fields': ('order', 'customer', 'customer_name', 'amount', 'paid_via', 'status')
        }),
        ('Transaction Details', {
            'fields': ('transaction_id', 'payment_date', 'notes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
