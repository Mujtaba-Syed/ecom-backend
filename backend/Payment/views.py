from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.db import IntegrityError, transaction
import logging
from .models import Payment
from .serializers import PaymentSerializer, PaymentCreateSerializer, PaymentUpdateSerializer
from Order.models import Order

logger = logging.getLogger(__name__)


class PaymentListView(generics.ListCreateAPIView):
    """List user's payments and create new payment"""
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Handle Swagger schema generation
        if getattr(self, 'swagger_fake_view', False) or not self.request.user.is_authenticated:
            return Payment.objects.none()
        
        # Regular users see only their payments, admins see all
        if self.request.user.is_staff:
            return Payment.objects.all()
        return Payment.objects.filter(customer=self.request.user)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return PaymentCreateSerializer
        return PaymentSerializer

    def create(self, request, *args, **kwargs):
        try:
            serializer = PaymentCreateSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            order_id = serializer.validated_data['order_id']
            amount = serializer.validated_data['amount']
            paid_via = serializer.validated_data.get('paid_via', 'credit_card')
            transaction_id = serializer.validated_data.get('transaction_id', '')
            notes = serializer.validated_data.get('notes', '')

            try:
                order = Order.objects.get(id=order_id)
            except Order.DoesNotExist:
                return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)
            except Exception as e:
                logger.error(f"Error fetching order: {str(e)}")
                return Response({'error': 'Error fetching order'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            # Verify order belongs to the user (unless admin)
            if not request.user.is_staff and order.user != request.user:
                return Response({'error': 'You do not have permission to create payment for this order'}, 
                              status=status.HTTP_403_FORBIDDEN)

            # Verify payment amount matches order total (with some tolerance for rounding)
            if abs(float(amount) - float(order.total_price)) > 0.01:
                return Response({'error': f'Payment amount (${amount}) does not match order total (${order.total_price})'}, 
                              status=status.HTTP_400_BAD_REQUEST)

            try:
                with transaction.atomic():
                    payment = Payment.objects.create(
                        order=order,
                        customer=request.user,
                        amount=amount,
                        paid_via=paid_via,
                        transaction_id=transaction_id,
                        notes=notes,
                        status='completed'  # Auto-complete on creation, can be updated later
                    )

                return Response(PaymentSerializer(payment).data, status=status.HTTP_201_CREATED)
            except IntegrityError as e:
                logger.error(f"Integrity error creating payment: {str(e)}")
                return Response({'error': 'Error creating payment'}, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                logger.error(f"Error creating payment: {str(e)}")
                return Response({'error': 'Error creating payment'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            logger.error(f"Unexpected error in payment creation: {str(e)}")
            return Response({'error': 'An unexpected error occurred'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PaymentDetailView(generics.RetrieveUpdateAPIView):
    """Get or update a specific payment"""
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Handle Swagger schema generation
        if getattr(self, 'swagger_fake_view', False) or not self.request.user.is_authenticated:
            return Payment.objects.none()
        
        # Regular users see only their payments, admins see all
        if self.request.user.is_staff:
            return Payment.objects.all()
        return Payment.objects.filter(customer=self.request.user)

    def get_serializer_class(self):
        if self.request.method in ['PATCH', 'PUT']:
            return PaymentUpdateSerializer
        return PaymentSerializer


class PaymentByOrderView(generics.ListAPIView):
    """Get all payments for a specific order"""
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        order_id = self.kwargs.get('order_id')
        if getattr(self, 'swagger_fake_view', False) or not self.request.user.is_authenticated:
            return Payment.objects.none()
        
        try:
            order = Order.objects.get(id=order_id)
            # Verify order belongs to the user (unless admin)
            if not self.request.user.is_staff and order.user != self.request.user:
                return Payment.objects.none()
            return Payment.objects.filter(order_id=order_id)
        except Order.DoesNotExist:
            return Payment.objects.none()
