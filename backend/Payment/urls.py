from django.urls import path
from .views import PaymentListView, PaymentDetailView, PaymentByOrderView

app_name = 'payment'

urlpatterns = [
    path('', PaymentListView.as_view(), name='payment-list'),
    path('<int:pk>/', PaymentDetailView.as_view(), name='payment-detail'),
    path('order/<int:order_id>/', PaymentByOrderView.as_view(), name='payment-by-order'),
]
