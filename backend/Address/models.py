from django.db import models
from django.conf import settings


class Address(models.Model):
    """Address model for storing user shipping addresses"""
    ADDRESS_TYPE_CHOICES = [
        ('home', 'Home'),
        ('work', 'Work'),
        ('other', 'Other'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='addresses')
    address_type = models.CharField(max_length=10, choices=ADDRESS_TYPE_CHOICES, default='home')
    full_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15)
    street_address = models.CharField(max_length=200)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100, default='United States')
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'address'
        verbose_name = 'Address'
        verbose_name_plural = 'Addresses'
        ordering = ['-is_default', '-created_at']

    def __str__(self):
        return f"{self.full_name} - {self.city}, {self.state}"

    def save(self, *args, **kwargs):
        # If this address is set as default, unset other default addresses for this user
        if self.is_default:
            Address.objects.filter(user=self.user, is_default=True).exclude(pk=self.pk).update(is_default=False)
        super().save(*args, **kwargs)
