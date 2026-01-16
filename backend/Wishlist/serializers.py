from rest_framework import serializers
from .models import Wishlist
from Products.serializers import ProductSerializer


class WishlistSerializer(serializers.ModelSerializer):
    """Serializer for Wishlist model"""
    product = ProductSerializer(read_only=True)

    class Meta:
        model = Wishlist
        fields = ('id', 'product', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')


class WishlistCreateSerializer(serializers.Serializer):
    """Serializer for creating wishlist items"""
    product_id = serializers.IntegerField()
