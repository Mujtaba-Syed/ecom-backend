from django.urls import path
from .views import CartListView, CartDetailView, CartQuantityUpdateView

app_name = 'cart'

urlpatterns = [
    path('', CartListView.as_view(), name='cart-list'),
    path('<int:pk>/', CartDetailView.as_view(), name='cart-detail'),
    path('<int:pk>/quantity/', CartQuantityUpdateView.as_view(), name='cart-quantity-update'),
]

