from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.db import IntegrityError
import logging
from .models import Product
from .serializers import ProductSerializer

logger = logging.getLogger(__name__)


class ProductDetailView(generics.RetrieveUpdateAPIView):
    """Get and update single product (for single product ecommerce)"""
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]
    lookup_field = 'id'

    def get_object(self):
        try:
            # For single product ecommerce, return the first product
            product, created = Product.objects.get_or_create(
                id=1,
                defaults={
                    'name': 'Default Product',
                    'description': 'Product description',
                    'price': 0.00,
                    'stock': 0,
                    'is_available': True
                }
            )
            return product
        except IntegrityError as e:
            logger.error(f"Integrity error fetching product: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error fetching product: {str(e)}")
            raise


class ProductListView(generics.ListAPIView):
    """List products (for single product, returns one product)"""
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]
