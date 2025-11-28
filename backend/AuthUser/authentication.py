from rest_framework_simplejwt.authentication import JWTAuthentication
from django.conf import settings


class CookieJWTAuthentication(JWTAuthentication):
    """
    Custom JWT Authentication that reads tokens from cookies instead of headers.
    Falls back to header-based authentication if cookies are not present.
    """
    
    def authenticate(self, request):
        # Try to get token from cookie first
        header = self.get_header(request)
        if header is None:
            # Try to get from cookie
            access_token = request.COOKIES.get(settings.SIMPLE_JWT.get('AUTH_COOKIE', 'access_token'))
            if access_token:
                # Set the token in the request header format for processing
                request.META['HTTP_AUTHORIZATION'] = f"Bearer {access_token}"
                header = self.get_header(request)
        
        if header is None:
            return None
        
        raw_token = self.get_raw_token(header)
        if raw_token is None:
            return None

        validated_token = self.get_validated_token(raw_token)
        return self.get_user(validated_token), validated_token

