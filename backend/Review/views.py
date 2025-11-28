from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.db import IntegrityError, transaction
import logging
from .models import Review
from .serializers import ReviewSerializer, ReviewCreateSerializer
from Products.models import Product

logger = logging.getLogger(__name__)


class ReviewListView(generics.ListCreateAPIView):
    """List all reviews and create new reviews"""
    serializer_class = ReviewSerializer

    def get_queryset(self):
        product_id = self.request.query_params.get('product_id', None)
        if product_id:
            return Review.objects.filter(product_id=product_id)
        return Review.objects.all()

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ReviewCreateSerializer
        return ReviewSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated()]
        return [AllowAny()]

    def create(self, request, *args, **kwargs):
        try:
            serializer = ReviewCreateSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            product_id = serializer.validated_data['product_id']
            rating = serializer.validated_data['rating']
            comment = serializer.validated_data['comment']

            try:
                product = Product.objects.get(id=product_id)
            except Product.DoesNotExist:
                return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)
            except Exception as e:
                logger.error(f"Error fetching product: {str(e)}")
                return Response({'error': 'Error fetching product'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            try:
                with transaction.atomic():
                    review, created = Review.objects.get_or_create(
                        user=request.user,
                        product=product,
                        defaults={'rating': rating, 'comment': comment}
                    )

                    if not created:
                        review.rating = rating
                        review.comment = comment
                        review.save()

                return Response(ReviewSerializer(review).data, status=status.HTTP_201_CREATED)
            except IntegrityError as e:
                logger.error(f"Integrity error creating review: {str(e)}")
                return Response({'error': 'Error creating review'}, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                logger.error(f"Error creating review: {str(e)}")
                return Response({'error': 'Error creating review'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            logger.error(f"Unexpected error in review creation: {str(e)}")
            return Response({'error': 'An unexpected error occurred'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ReviewDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Get, update, or delete a specific review"""
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Handle Swagger schema generation
        if getattr(self, 'swagger_fake_view', False) or not self.request.user.is_authenticated:
            return Review.objects.none()
        if self.request.user.is_staff:
            return Review.objects.all()
        return Review.objects.filter(user=self.request.user)
