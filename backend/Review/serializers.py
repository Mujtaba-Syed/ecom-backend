from rest_framework import serializers
from .models import Review
from AuthUser.serializers import UserSerializer
from Products.serializers import ProductSerializer


class ReviewSerializer(serializers.ModelSerializer):
    """Serializer for Review model"""
    user = UserSerializer(read_only=True)
    product = ProductSerializer(read_only=True)

    class Meta:
        model = Review
        fields = ('id', 'user', 'product', 'rating', 'comment', 'created_at', 'updated_at')
        read_only_fields = ('id', 'user', 'created_at', 'updated_at')


class ReviewCreateSerializer(serializers.Serializer):
    """Serializer for creating reviews"""
    product_id = serializers.IntegerField()
    rating = serializers.IntegerField(min_value=1, max_value=5)
    comment = serializers.CharField()

