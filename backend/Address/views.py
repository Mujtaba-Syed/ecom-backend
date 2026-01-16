from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import IntegrityError
import logging
from .models import Address
from .serializers import AddressSerializer

logger = logging.getLogger(__name__)


class AddressListView(generics.ListCreateAPIView):
    """List user's addresses and create new address"""
    serializer_class = AddressSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Handle Swagger schema generation
        if getattr(self, 'swagger_fake_view', False) or not self.request.user.is_authenticated:
            return Address.objects.none()
        return Address.objects.filter(user=self.request.user)


class AddressDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Get, update, or delete a specific address"""
    serializer_class = AddressSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Handle Swagger schema generation
        if getattr(self, 'swagger_fake_view', False) or not self.request.user.is_authenticated:
            return Address.objects.none()
        return Address.objects.filter(user=self.request.user)


class AddressSetDefaultView(generics.GenericAPIView):
    """Set an address as default"""
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False) or not self.request.user.is_authenticated:
            return Address.objects.none()
        return Address.objects.filter(user=self.request.user)

    def patch(self, request, pk):
        """Set address as default"""
        try:
            try:
                address = Address.objects.get(pk=pk, user=request.user)
            except Address.DoesNotExist:
                return Response({'error': 'Address not found'}, status=status.HTTP_404_NOT_FOUND)
            except Exception as e:
                logger.error(f"Error fetching address: {str(e)}")
                return Response({'error': 'Error fetching address'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            try:
                address.is_default = True
                address.save()
                return Response(AddressSerializer(address).data, status=status.HTTP_200_OK)
            except Exception as e:
                logger.error(f"Error updating address: {str(e)}")
                return Response({'error': 'Error updating address'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            logger.error(f"Unexpected error in address update: {str(e)}")
            return Response({'error': 'An unexpected error occurred'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
