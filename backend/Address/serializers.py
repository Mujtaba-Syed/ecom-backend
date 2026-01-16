from rest_framework import serializers
from .models import Address


class AddressSerializer(serializers.ModelSerializer):
    """Serializer for Address model"""
    class Meta:
        model = Address
        fields = ('id', 'address_type', 'full_name', 'phone_number', 'street_address', 
                 'city', 'state', 'postal_code', 'country', 'is_default', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')
