from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.exceptions import ValidationError
from django.contrib.auth import authenticate
from django.db import IntegrityError
from django.conf import settings
from rest_framework_simplejwt.tokens import RefreshToken
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
import logging
from .models import User
from .serializers import UserRegistrationSerializer, UserSerializer, UserLoginSerializer

logger = logging.getLogger(__name__)


class UserRegistrationView(generics.CreateAPIView):
    """
    User Registration
    
    Register a new user account. Returns user data and authentication token.
    """
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description="Register a new user. JWT tokens are automatically stored in HttpOnly cookies and also returned in response body.",
        responses={
            201: openapi.Response(
                'User created successfully - tokens in cookies and response',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'user': openapi.Schema(type=openapi.TYPE_OBJECT),
                        'access': openapi.Schema(type=openapi.TYPE_STRING, description='JWT Access Token'),
                        'refresh': openapi.Schema(type=openapi.TYPE_STRING, description='JWT Refresh Token'),
                        'message': openapi.Schema(type=openapi.TYPE_STRING, description='Success message')
                    }
                )
            ),
            400: 'Bad request - validation error'
        }
    )

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            try:
                user = serializer.save()
            except IntegrityError as e:
                logger.error(f"Integrity error during user registration: {str(e)}")
                return Response({'error': 'Username or email already exists'}, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                logger.error(f"Error creating user: {str(e)}")
                return Response({'error': f'Error creating user account: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            try:
                # Generate JWT tokens
                refresh = RefreshToken.for_user(user)
                access_token = refresh.access_token
            except Exception as e:
                logger.error(f"Error creating JWT tokens: {str(e)}")
                return Response({'error': f'Error generating authentication tokens: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            # Create response with tokens in body
            response = Response({
                'user': UserSerializer(user).data,
                'access': str(access_token),
                'refresh': str(refresh),
                'message': 'Registration successful. Tokens stored in cookies and returned in response.'
            }, status=status.HTTP_201_CREATED)
            
            # Set cookies
            response.set_cookie(
                key=settings.SIMPLE_JWT['AUTH_COOKIE'],
                value=str(access_token),
                max_age=settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'].total_seconds(),
                httponly=settings.SIMPLE_JWT['AUTH_COOKIE_HTTP_ONLY'],
                samesite=settings.SIMPLE_JWT['AUTH_COOKIE_SAMESITE'],
                secure=settings.SIMPLE_JWT['AUTH_COOKIE_SECURE'],
            )
            response.set_cookie(
                key=settings.SIMPLE_JWT['AUTH_COOKIE_REFRESH'],
                value=str(refresh),
                max_age=settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'].total_seconds(),
                httponly=settings.SIMPLE_JWT['AUTH_COOKIE_HTTP_ONLY'],
                samesite=settings.SIMPLE_JWT['AUTH_COOKIE_SAMESITE'],
                secure=settings.SIMPLE_JWT['AUTH_COOKIE_SECURE'],
            )
            
            return response
        except ValidationError as e:
            # Handle validation errors properly
            logger.error(f"Validation error in user registration: {e.detail}")
            return Response({'error': e.detail}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Unexpected error in user registration: {str(e)}")
            return Response({'error': f'An unexpected error occurred during registration: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserLoginView(generics.GenericAPIView):
    """
    User Login
    
    Authenticate user and get authentication token.
    """
    serializer_class = UserLoginSerializer
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description="Login user. JWT tokens are automatically stored in HttpOnly cookies and also returned in response body.",
        responses={
            200: openapi.Response(
                'Login successful - tokens in cookies and response',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'user': openapi.Schema(type=openapi.TYPE_OBJECT),
                        'access': openapi.Schema(type=openapi.TYPE_STRING, description='JWT Access Token'),
                        'refresh': openapi.Schema(type=openapi.TYPE_STRING, description='JWT Refresh Token'),
                        'message': openapi.Schema(type=openapi.TYPE_STRING, description='Success message')
                    }
                )
            ),
            401: 'Invalid credentials'
        }
    )
    def post(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']
            
            try:
                user = authenticate(username=username, password=password)
            except Exception as e:
                logger.error(f"Error during authentication: {str(e)}")
                return Response({'error': f'Authentication error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            if user:
                try:
                    # Generate JWT tokens
                    refresh = RefreshToken.for_user(user)
                    access_token = refresh.access_token
                    
                    # Create response with tokens in body
                    response = Response({
                        'user': UserSerializer(user).data,
                        'access': str(access_token),
                        'refresh': str(refresh),
                        'message': 'Login successful. Tokens stored in cookies and returned in response.'
                    }, status=status.HTTP_200_OK)
                    
                    # Set cookies
                    response.set_cookie(
                        key=settings.SIMPLE_JWT['AUTH_COOKIE'],
                        value=str(access_token),
                        max_age=settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'].total_seconds(),
                        httponly=settings.SIMPLE_JWT['AUTH_COOKIE_HTTP_ONLY'],
                        samesite=settings.SIMPLE_JWT['AUTH_COOKIE_SAMESITE'],
                        secure=settings.SIMPLE_JWT['AUTH_COOKIE_SECURE'],
                    )
                    response.set_cookie(
                        key=settings.SIMPLE_JWT['AUTH_COOKIE_REFRESH'],
                        value=str(refresh),
                        max_age=settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'].total_seconds(),
                        httponly=settings.SIMPLE_JWT['AUTH_COOKIE_HTTP_ONLY'],
                        samesite=settings.SIMPLE_JWT['AUTH_COOKIE_SAMESITE'],
                        secure=settings.SIMPLE_JWT['AUTH_COOKIE_SECURE'],
                    )
                    
                    return response
                except Exception as e:
                    logger.error(f"Error creating JWT tokens: {str(e)}")
                    return Response({'error': f'Error generating authentication tokens: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        except ValidationError as e:
            # Handle validation errors properly
            logger.error(f"Validation error in user login: {e.detail}")
            return Response({'error': e.detail}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Unexpected error in user login: {str(e)}")
            return Response({'error': f'An unexpected error occurred during login: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    User Profile
    
    Get or update authenticated user's profile information.
    Requires authentication token.
    """
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Get current user profile",
        responses={
            200: UserSerializer,
            401: 'Authentication required'
        }
    )
    def get(self, request, *args, **kwargs):
        try:
            return super().get(request, *args, **kwargs)
        except Exception as e:
            logger.error(f"Error fetching user profile: {str(e)}")
            return Response({'error': 'Error fetching user profile'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @swagger_auto_schema(
        operation_description="Update current user profile",
        responses={
            200: UserSerializer,
            400: 'Bad request - validation error',
            401: 'Authentication required'
        }
    )
    def put(self, request, *args, **kwargs):
        try:
            return super().put(request, *args, **kwargs)
        except IntegrityError as e:
            logger.error(f"Integrity error updating user profile: {str(e)}")
            return Response({'error': 'Username or email already exists'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error updating user profile: {str(e)}")
            return Response({'error': 'Error updating user profile'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get_object(self):
        return self.request.user


class UserLogoutView(generics.GenericAPIView):
    """
    User Logout
    
    Logout user by blacklisting refresh token and deleting authentication cookies.
    Cookies are automatically deleted by the backend.
    """
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description="Logout user. Refresh token is blacklisted and cookies are automatically deleted.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'refresh': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='(Optional) Refresh token to blacklist. If not provided, cookies will still be deleted.'
                )
            },
            required=[]
        ),
        responses={
            200: 'Logout successful - cookies deleted'
        }
    )
    def post(self, request, *args, **kwargs):
        try:
            # Get refresh token from request body or cookie
            refresh_token = request.data.get('refresh') or request.COOKIES.get(settings.SIMPLE_JWT['AUTH_COOKIE_REFRESH'])
            
            # Try to blacklist the refresh token if provided
            if refresh_token:
                try:
                    token = RefreshToken(refresh_token)
                    token.blacklist()
                except Exception as e:
                    error_msg = str(e)
                    logger.error(f"Error blacklisting token: {error_msg}")
                    # Continue even if blacklisting fails (token might already be invalid)
            
            # Create response
            response = Response({
                'message': 'Successfully logged out. Cookies deleted.'
            }, status=status.HTTP_200_OK)
            
            # Delete cookies by setting them with max_age=0
            response.set_cookie(
                key=settings.SIMPLE_JWT['AUTH_COOKIE'],
                value='',
                max_age=0,
                httponly=settings.SIMPLE_JWT['AUTH_COOKIE_HTTP_ONLY'],
                samesite=settings.SIMPLE_JWT['AUTH_COOKIE_SAMESITE'],
                secure=settings.SIMPLE_JWT['AUTH_COOKIE_SECURE'],
            )
            response.set_cookie(
                key=settings.SIMPLE_JWT['AUTH_COOKIE_REFRESH'],
                value='',
                max_age=0,
                httponly=settings.SIMPLE_JWT['AUTH_COOKIE_HTTP_ONLY'],
                samesite=settings.SIMPLE_JWT['AUTH_COOKIE_SAMESITE'],
                secure=settings.SIMPLE_JWT['AUTH_COOKIE_SECURE'],
            )
            
            return response
        except Exception as e:
            logger.error(f"Unexpected error in user logout: {str(e)}")
            return Response({'error': f'An unexpected error occurred during logout: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)