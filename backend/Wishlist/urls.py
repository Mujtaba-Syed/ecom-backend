from django.urls import path
from .views import WishlistListView, WishlistDetailView

app_name = 'wishlist'

urlpatterns = [
    path('', WishlistListView.as_view(), name='wishlist-list'),
    path('<int:pk>/', WishlistDetailView.as_view(), name='wishlist-detail'),
]
