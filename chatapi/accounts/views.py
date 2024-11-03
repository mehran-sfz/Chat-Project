from django.utils import timezone
from rest_framework.views import APIView
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated

from .models import User, Profile
import accounts.serializers as serializers
from .utils import generate_otp, otp_expiry
from uuid import uuid4
from .sender import send_otp

# login with OTP
class UserViewSet(viewsets.ViewSet):
    queryset = User.objects.all()

    @action(detail=False, methods=['POST'], url_path='generate-otp')
    def generate_otp(self, request):
        serializer = serializers.OTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone_number = serializer.validated_data['phone_number']
        user, created = User.objects.get_or_create(phone_number=phone_number)
        
        if created:
            Profile.objects.create(user=user)

        # Check if an OTP exists and is still valid
        if user.otp and timezone.now() < user.otp_expiry:
            otp = user.otp

        else:
            # Generate a new OTP, request ID, and expiry
            otp = generate_otp()
            user.otp = otp
            user.otp_expiry = otp_expiry()
            user.otp_request_id = uuid4()  # Generate new request ID
            user.save()

        # Placeholder for OTP sending (e.g., SMS)
        send_otp(otp=otp, phone_number=phone_number)

        return Response(
            {
                "message": "OTP sent successfully",
                "request_id": str(user.otp_request_id)
            },
            status=status.HTTP_200_OK)


    @action(detail=False, methods=['POST'], url_path='verify-otp')
    def verify_otp(self, request):
        serializer = serializers.OTPVerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone_number = serializer.validated_data['phone_number']
        otp = serializer.validated_data['otp']
        request_id = serializer.validated_data.get('request_id')

        try:
            user = User.objects.get(phone_number=phone_number)
            # print(user.otp == otp , timezone.now() < user.otp_expiry ,user.otp_request_id == request_id )
            if (
                user.otp == otp and # Verify OTP
                timezone.now() < user.otp_expiry and # Verify OTP expiry
                user.otp_request_id == request_id  # Verify request ID
            ):
                user.is_active = True
                user.save()

                # JWT token creation
                refresh = RefreshToken.for_user(user)

                return Response({
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                    "message": "OTP verified successfully"
                }, status=status.HTTP_200_OK)
            else:
                return Response({"error": "Invalid or expired OTP or request ID"}, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

# edit profile
class ProfileView(APIView):
    
    permission_classes = [IsAuthenticated]
    
    def get_object(self, user):
        try:
            return Profile.objects.get(user=user)
        except Profile.DoesNotExist:
            return None
        
    def get(self, request, *args, **kwargs):
        profile = self.get_object(request.user)
        if profile:
            serializer = serializers.ProfileSerializer(profile)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        return Response({"error": "Profile not found"}, status=status.HTTP_404_NOT_FOUND)
    
    
    def post(self, request, *args, **kwargs):
        profile = self.get_object(request.user)
        if not profile:
            serializer = serializers.ProfileSerializer(data=request.data, context={'user': request.user})
            serializer.is_valid(raise_exception=True)
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response({"error": "Profile already exists"}, status=status.HTTP_400_BAD_REQUEST)
    
        
    def put(self, request, *args, **kwargs):
        profile = self.get_object(request.user)
        if profile:
            serializer = serializers.ProfileSerializer(profile, data=request.data, context={'user': request.user})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AdminProfileView(APIView):
    
    permission_classes = [IsAuthenticated]
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return Response({"error": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)
        return super().dispatch(request, *args, **kwargs)
    
    def get(self, request, *args, **kwargs):
        
        phone_number = request.query_params.get('phone_number', None)
        username = request.query_params.get('username', None)
        
        profiles = Profile.objects.all()
        if phone_number:
            profiles = profiles.filter(user__phone_number=phone_number)
        elif username:
            profiles = profiles.filter(username=username)
            
        serializer = serializers.ProfileSerializer(profiles, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    