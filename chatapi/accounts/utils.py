import random
from datetime import timedelta
from django.utils import timezone
import os

def generate_otp():
    return random.randint(100000, 999999)

def otp_expiry():
    return timezone.now() + timedelta(minutes=5)


def user_avatar_upload_path(instance, filename):
    # Get the user's phone number from the related User model
    phone_number = instance.user.phone_number
    # Get the file extension of the original uploaded file
    ext = filename.split('.')[-1]
    # Create a new filename with the user's phone number and original extension
    filename = f"{phone_number}.{ext}"
    # Return the full path where the file will be uploaded
    return os.path.join('avatars/', filename)