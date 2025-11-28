from rest_framework import serializers
from .models import Order
from Products.serializers import ProductSerializer


class OrderSerializer(serializers.ModelSerializer):
    """Serializer for Order model"""
    product = ProductSerializer(read_only=True)

    class Meta:
        model = Order
        fields = ('id', 'user', 'product', 'quantity', 'total_price', 'status', 'shipping_address', 'created_at', 'updated_at')
        read_only_fields = ('id', 'user', 'created_at', 'updated_at')


class OrderCreateSerializer(serializers.Serializer):
    """Serializer for creating orders"""
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1)
    shipping_address = serializers.CharField()

