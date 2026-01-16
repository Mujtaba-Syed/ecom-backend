from rest_framework import serializers
from .models import Payment
from Order.serializers import OrderSerializer
from AuthUser.serializers import UserSerializer


class PaymentSerializer(serializers.ModelSerializer):
    """Serializer for Payment model"""
    order = OrderSerializer(read_only=True)
    customer = UserSerializer(read_only=True)
    customer_name = serializers.CharField(read_only=True)

    class Meta:
        model = Payment
        fields = ('id', 'order', 'customer', 'customer_name', 'amount', 'paid_via', 'status', 
                 'transaction_id', 'payment_date', 'notes', 'created_at', 'updated_at')
        read_only_fields = ('id', 'customer', 'customer_name', 'payment_date', 'created_at', 'updated_at')


class PaymentCreateSerializer(serializers.Serializer):
    """Serializer for creating payments"""
    order_id = serializers.IntegerField()
    amount = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=0)
    paid_via = serializers.ChoiceField(
        choices=[
            ('credit_card', 'Credit Card'),
            ('debit_card', 'Debit Card'),
            ('paypal', 'PayPal'),
            ('bank_transfer', 'Bank Transfer'),
            ('cash_on_delivery', 'Cash on Delivery'),
            ('stripe', 'Stripe'),
            ('razorpay', 'Razorpay'),
            ('other', 'Other'),
        ],
        default='credit_card'
    )
    transaction_id = serializers.CharField(max_length=200, required=False, allow_blank=True)
    notes = serializers.CharField(required=False, allow_blank=True)


class PaymentUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating payment status"""
    class Meta:
        model = Payment
        fields = ('status', 'transaction_id', 'notes')
        read_only_fields = ('id', 'order', 'customer', 'customer_name', 'amount', 'paid_via', 'payment_date', 'created_at', 'updated_at')
