from django.urls import path
from .views import ReviewListView, ReviewDetailView

app_name = 'review'

urlpatterns = [
    path('', ReviewListView.as_view(), name='review-list'),
    path('<int:pk>/', ReviewDetailView.as_view(), name='review-detail'),
]

