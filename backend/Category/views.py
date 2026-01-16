from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
import logging
from .models import Category
from .serializers import CategorySerializer

logger = logging.getLogger(__name__)


class CategoryListView(generics.ListCreateAPIView):
    """List all categories and create new category (admin only)"""
    queryset = Category.objects.filter(is_active=True)
    serializer_class = CategorySerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAdminUser()]
        return [AllowAny()]

    def get_queryset(self):
        if self.request.method == 'GET':
            # Public can only see active categories
            return Category.objects.filter(is_active=True)
        # Admin can see all categories when creating
        return Category.objects.all()


class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Get, update, or delete a specific category"""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminUser]
    lookup_field = 'id'

    def perform_destroy(self, instance):
        # Soft delete - set is_active to False instead of deleting
        instance.is_active = False
        instance.save()
