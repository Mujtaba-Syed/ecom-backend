from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import IntegrityError, transaction
import logging
from .models import Order
from .serializers import OrderSerializer, OrderCreateSerializer
from Products.models import Product

logger = logging.getLogger(__name__)


class OrderListView(generics.ListCreateAPIView):
    """List user's orders and create new orders"""
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Handle Swagger schema generation
        if getattr(self, 'swagger_fake_view', False) or not self.request.user.is_authenticated:
            return Order.objects.none()
        return Order.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return OrderCreateSerializer
        return OrderSerializer

    def create(self, request, *args, **kwargs):
        try:
            serializer = OrderCreateSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            product_id = serializer.validated_data['product_id']
            quantity = serializer.validated_data['quantity']
            shipping_address = serializer.validated_data['shipping_address']

            try:
                product = Product.objects.get(id=product_id)
            except Product.DoesNotExist:
                return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)
            except Exception as e:
                logger.error(f"Error fetching product: {str(e)}")
                return Response({'error': 'Error fetching product'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            if product.stock < quantity:
                return Response({'error': 'Insufficient stock'}, status=status.HTTP_400_BAD_REQUEST)

            try:
                with transaction.atomic():
                    total_price = product.price * quantity
                    order = Order.objects.create(
                        user=request.user,
                        product=product,
                        quantity=quantity,
                        total_price=total_price,
                        shipping_address=shipping_address
                    )

                    # Update product stock
                    product.stock -= quantity
                    product.save()

                return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)
            except IntegrityError as e:
                logger.error(f"Integrity error creating order: {str(e)}")
                return Response({'error': 'Error creating order'}, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                logger.error(f"Error creating order: {str(e)}")
                return Response({'error': 'Error creating order'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            logger.error(f"Unexpected error in order creation: {str(e)}")
            return Response({'error': 'An unexpected error occurred'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class OrderDetailView(generics.RetrieveUpdateAPIView):
    """Get and update a specific order"""
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Handle Swagger schema generation
        if getattr(self, 'swagger_fake_view', False) or not self.request.user.is_authenticated:
            return Order.objects.none()
        return Order.objects.filter(user=self.request.user)
