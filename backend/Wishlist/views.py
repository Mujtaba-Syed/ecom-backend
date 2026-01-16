from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import IntegrityError
import logging
from .models import Wishlist
from .serializers import WishlistSerializer, WishlistCreateSerializer
from Products.models import Product

logger = logging.getLogger(__name__)


class WishlistListView(generics.ListCreateAPIView):
    """List user's wishlist items and add items to wishlist"""
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Handle Swagger schema generation
        if getattr(self, 'swagger_fake_view', False) or not self.request.user.is_authenticated:
            return Wishlist.objects.none()
        return Wishlist.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return WishlistCreateSerializer
        return WishlistSerializer

    def create(self, request, *args, **kwargs):
        try:
            serializer = WishlistCreateSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            product_id = serializer.validated_data['product_id']

            try:
                product = Product.objects.get(id=product_id)
            except Product.DoesNotExist:
                return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)
            except Exception as e:
                logger.error(f"Error fetching product: {str(e)}")
                return Response({'error': 'Error fetching product'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            try:
                wishlist_item, created = Wishlist.objects.get_or_create(
                    user=request.user,
                    product=product
                )

                if not created:
                    return Response({'error': 'Product already in wishlist'}, status=status.HTTP_400_BAD_REQUEST)

                return Response(WishlistSerializer(wishlist_item).data, status=status.HTTP_201_CREATED)
            except IntegrityError as e:
                logger.error(f"Integrity error creating wishlist item: {str(e)}")
                return Response({'error': 'Error adding item to wishlist'}, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                logger.error(f"Error creating wishlist item: {str(e)}")
                return Response({'error': 'Error adding item to wishlist'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            logger.error(f"Unexpected error in wishlist create: {str(e)}")
            return Response({'error': 'An unexpected error occurred'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class WishlistDetailView(generics.RetrieveDestroyAPIView):
    """Get or delete a specific wishlist item"""
    serializer_class = WishlistSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Handle Swagger schema generation
        if getattr(self, 'swagger_fake_view', False) or not self.request.user.is_authenticated:
            return Wishlist.objects.none()
        return Wishlist.objects.filter(user=self.request.user)
