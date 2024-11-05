from rest_framework import serializers
from .models import User, Profile
import re
from django.utils import timezone

# -------------- login with OTP --------------

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['phone_number', 'is_active']

# class ProfileSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Profile
#         fields = [
#             'email', 'first_name', 'last_name', 'username',
#             'nationality_number', 'avatar', 'birth_date',
#         ]

class OTPSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=15)

class OTPVerifySerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=15)
    otp = serializers.CharField(max_length=6)
    request_id = serializers.UUIDField()
       
    
    
# -------------- Profile --------------
class ProfileSerializer(serializers.ModelSerializer):
    
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    
    class Meta:
        model = Profile
        fields = [
            'id', 'user', 'email', 'first_name', 'last_name', 'username',
            'nationality_number', 'avatar', 'birth_date',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
     
    def validate(self, data):
        # Check if the user has a profile
        user = self.context.get('user')
        if not user.profile:
            raise serializers.ValidationError("User profile does not exist")

        email = data.get('email')
        if email:
            # Check if the email is unique
            if Profile.objects.filter(email=email).exclude(user=user).exists():
                raise serializers.ValidationError("Email already exists")
    
        nationality_number = data.get('nationality_number')
        if nationality_number:
            # sould be all digits and unique
            if not re.match(r'^\d+$'):
                raise serializers.ValidationError("Nationality number should be all digits")
            elif Profile.objects.filter(nationality_number=nationality_number).exclude(user=user).exists():
                raise serializers.ValidationError("Nationality number should be unique")
    
        # Check if the avatar is an image file (png, jpg, jpeg)
        avatar = data.get('avatar')
        if avatar:
            if not avatar.name.endswith(('.png', '.jpg', '.jpeg')):
                raise serializers.ValidationError("Avatar should be an image file")
            
            
        birth_date = data.get('birth_date')
        if birth_date:
            # Check if the birth date is valid
            if birth_date > timezone.now().date():
                raise serializers.ValidationError("Birth date should be in the past")
    
        return data
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    