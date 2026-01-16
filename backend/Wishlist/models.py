from django.db import models
from django.conf import settings
from Products.models import Product


class Wishlist(models.Model):
    """Wishlist model for storing user's saved products"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='wishlists')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='wishlist_items')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'wishlist'
        verbose_name = 'Wishlist'
        verbose_name_plural = 'Wishlists'
        unique_together = ['user', 'product']
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.product.name}"
