from rest_framework import serializers
from .models import Order
from Products.serializers import ProductSerializer
from Address.serializers import AddressSerializer


class OrderSerializer(serializers.ModelSerializer):
    """Serializer for Order model"""
    product = ProductSerializer(read_only=True)
    shipping_address_obj = AddressSerializer(source='shipping_address', read_only=True)

    class Meta:
        model = Order
        fields = ('id', 'user', 'product', 'quantity', 'total_price', 'status', 
                 'shipping_address', 'shipping_address_obj', 'shipping_address_text', 
                 'created_at', 'updated_at')
        read_only_fields = ('id', 'user', 'created_at', 'updated_at')


class OrderCreateSerializer(serializers.Serializer):
    """Serializer for creating orders"""
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1)
    shipping_address_id = serializers.IntegerField(required=False, allow_null=True, help_text="ID of saved address from Address model")
    shipping_address = serializers.CharField(required=False, allow_blank=True, help_text="Text address (used if shipping_address_id is not provided)")

