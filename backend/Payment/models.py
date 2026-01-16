from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from Order.models import Order


class Payment(models.Model):
    """Payment model for storing payment transactions"""
    PAYMENT_METHOD_CHOICES = [
        ('credit_card', 'Credit Card'),
        ('debit_card', 'Debit Card'),
        ('paypal', 'PayPal'),
        ('bank_transfer', 'Bank Transfer'),
        ('cash_on_delivery', 'Cash on Delivery'),
        ('stripe', 'Stripe'),
        ('razorpay', 'Razorpay'),
        ('other', 'Other'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
        ('cancelled', 'Cancelled'),
    ]

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='payments')
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='payments')
    customer_name = models.CharField(max_length=200, help_text="Customer name at time of payment")
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    paid_via = models.CharField(max_length=50, choices=PAYMENT_METHOD_CHOICES, default='credit_card')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    transaction_id = models.CharField(max_length=200, blank=True, null=True, help_text="Payment gateway transaction ID")
    payment_date = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True, null=True, help_text="Additional payment notes")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'payment'
        verbose_name = 'Payment'
        verbose_name_plural = 'Payments'
        ordering = ['-payment_date', '-created_at']

    def __str__(self):
        return f"Payment #{self.id} - {self.customer_name} - ${self.amount}"

    def save(self, *args, **kwargs):
        # Auto-populate customer_name from customer if not provided
        if not self.customer_name and self.customer:
            self.customer_name = f"{self.customer.first_name} {self.customer.last_name}".strip() or self.customer.username
        super().save(*args, **kwargs)
