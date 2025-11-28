from rest_framework import serializers
from .models import Cart
from Products.serializers import ProductSerializer


class CartSerializer(serializers.ModelSerializer):
    """Serializer for Cart model"""
    product = ProductSerializer(read_only=True)
    total_price = serializers.ReadOnlyField()

    class Meta:
        model = Cart
        fields = ('id', 'product', 'quantity', 'total_price', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')


class CartCreateSerializer(serializers.Serializer):
    """Serializer for creating cart items"""
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(default=1, min_value=1)


class CartQuantityUpdateSerializer(serializers.Serializer):
    """Serializer for updating cart item quantity"""
    action = serializers.ChoiceField(choices=['increase', 'decrease'], required=True)
    quantity = serializers.IntegerField(default=1, min_value=1)

