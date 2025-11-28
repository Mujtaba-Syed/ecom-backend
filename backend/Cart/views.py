from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db import IntegrityError, transaction
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
import logging
from .models import Cart
from .serializers import CartSerializer, CartCreateSerializer, CartQuantityUpdateSerializer
from Products.models import Product

logger = logging.getLogger(__name__)


class CartListView(generics.ListCreateAPIView):
    """List user's cart items and add items to cart"""
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Handle Swagger schema generation
        if getattr(self, 'swagger_fake_view', False) or not self.request.user.is_authenticated:
            return Cart.objects.none()
        return Cart.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CartCreateSerializer
        return CartSerializer

    def create(self, request, *args, **kwargs):
        try:
            serializer = CartCreateSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            product_id = serializer.validated_data['product_id']
            quantity = serializer.validated_data.get('quantity', 1)

            try:
                product = Product.objects.get(id=product_id)
            except Product.DoesNotExist:
                return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)
            except Exception as e:
                logger.error(f"Error fetching product: {str(e)}")
                return Response({'error': 'Error fetching product'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            try:
                with transaction.atomic():
                    cart_item, created = Cart.objects.get_or_create(
                        user=request.user,
                        product=product,
                        defaults={'quantity': quantity}
                    )

                    if not created:
                        cart_item.quantity += quantity
                        cart_item.save()

                return Response(CartSerializer(cart_item).data, status=status.HTTP_201_CREATED)
            except IntegrityError as e:
                logger.error(f"Integrity error creating cart item: {str(e)}")
                return Response({'error': 'Error adding item to cart'}, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                logger.error(f"Error creating cart item: {str(e)}")
                return Response({'error': 'Error adding item to cart'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            logger.error(f"Unexpected error in cart create: {str(e)}")
            return Response({'error': 'An unexpected error occurred'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CartDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Get, update, or delete a specific cart item"""
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Handle Swagger schema generation
        if getattr(self, 'swagger_fake_view', False) or not self.request.user.is_authenticated:
            return Cart.objects.none()
        return Cart.objects.filter(user=self.request.user)


class CartQuantityUpdateView(generics.GenericAPIView):
    """
    Update Cart Item Quantity
    
    Increase or decrease the quantity of a cart item.
    - action: 'increase' or 'decrease'
    - quantity: amount to increase/decrease (default: 1)
    """
    serializer_class = CartQuantityUpdateSerializer
    permission_classes = [IsAuthenticated]
    queryset = Cart.objects.none()  # For Swagger schema generation

    def get_queryset(self):
        # Handle Swagger schema generation
        if getattr(self, 'swagger_fake_view', False) or not self.request.user.is_authenticated:
            return Cart.objects.none()
        return Cart.objects.filter(user=self.request.user)

    @swagger_auto_schema(
        operation_description="Update cart item quantity by increasing or decreasing",
        request_body=CartQuantityUpdateSerializer,
        responses={
            200: openapi.Response('Quantity updated successfully', CartSerializer),
            400: 'Bad request - validation error',
            404: 'Cart item not found',
            401: 'Authentication required'
        }
    )
    def patch(self, request, pk):
        """Update cart item quantity"""
        try:
            try:
                cart_item = Cart.objects.get(pk=pk, user=request.user)
            except Cart.DoesNotExist:
                return Response({'error': 'Cart item not found'}, status=status.HTTP_404_NOT_FOUND)
            except Exception as e:
                logger.error(f"Error fetching cart item: {str(e)}")
                return Response({'error': 'Error fetching cart item'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            action = serializer.validated_data['action']
            quantity = serializer.validated_data.get('quantity', 1)
            
            try:
                if action == 'increase':
                    cart_item.quantity += quantity
                elif action == 'decrease':
                    cart_item.quantity -= quantity
                    if cart_item.quantity < 1:
                        cart_item.quantity = 1
                
                cart_item.save()
                return Response(CartSerializer(cart_item).data, status=status.HTTP_200_OK)
            except Exception as e:
                logger.error(f"Error updating cart item quantity: {str(e)}")
                return Response({'error': 'Error updating cart item quantity'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            logger.error(f"Unexpected error in cart quantity update: {str(e)}")
            return Response({'error': 'An unexpected error occurred'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
