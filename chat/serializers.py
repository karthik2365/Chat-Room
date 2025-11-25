# # chat/serializers.py
# from rest_framework import serializers
# from django.contrib.auth import get_user_model
# from .models import UserProfile, Message

# User = get_user_model()


# class BasicUserSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = User
#         fields = ("id", "username", "email")
#         read_only_fields = ("id", "username", "email")


# # This is the serializer name your views expected: returns id, username, public_key
# class UserPublicSerializer(serializers.Serializer):
#     id = serializers.IntegerField(read_only=True)
#     username = serializers.CharField(read_only=True)
#     public_key = serializers.CharField(allow_null=True, allow_blank=True)

#     @classmethod
#     def from_user(cls, user):
#         try:
#             pk = user.profile.public_key
#         except Exception:
#             # fallback if relation name is different or profile missing
#             try:
#                 pk = user.userprofile.public_key
#             except Exception:
#                 pk = None
#         return cls({"id": user.id, "username": user.username, "public_key": pk})


# # ModelSerializer to update/save the public key for request.user
# class UserPublicKeySerializer(serializers.ModelSerializer):
#     class Meta:
#         model = UserProfile
#         fields = ("public_key",)


# # Update serializer name some views may import
# class UserPublicKeyUpdateSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = UserProfile
#         fields = ("public_key",)


# # Read serializer that exposes the user id, username and public_key together
# class UserPublicKeyReadSerializer(serializers.ModelSerializer):
#     id = serializers.IntegerField(source="user.id", read_only=True)
#     username = serializers.CharField(source="user.username", read_only=True)

#     class Meta:
#         model = UserProfile
#         fields = ("id", "username", "public_key")


# # Message serializer for REST use (if needed)
# class MessageSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Message
#         fields = ("id", "sender", "receiver", "ciphertext", "created_at")
#         read_only_fields = ("id", "created_at")




from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import UserProfile

User = get_user_model()

class UserPublicSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username"]


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ["user", "public_key"]


class UserPublicKeySerializer(serializers.ModelSerializer):
    """
    Used for GET: return only the public key of user <id>.
    """
    class Meta:
        model = UserProfile
        fields = ["public_key"]


class UserPublicKeyUpdateSerializer(serializers.ModelSerializer):
    """
    Used for POST: update current user’s public key.
    """
    class Meta:
        model = UserProfile
        fields = ["public_key"]