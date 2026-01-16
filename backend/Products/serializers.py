from rest_framework import serializers
from .models import Product


class ProductSerializer(serializers.ModelSerializer):
    """Serializer for Product model"""
    category_name = serializers.CharField(source='category.name', read_only=True)
    
    class Meta:
        model = Product
        fields = ('id', 'name', 'description', 'price', 'stock', 'image', 'category', 'category_name', 'is_available', 'created_at', 'updated_at')
        read_only_fields = ('id', 'category_name', 'created_at', 'updated_at')

