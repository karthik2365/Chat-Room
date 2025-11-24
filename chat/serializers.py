from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserProfile


class UserPublicSerializer(serializers.ModelSerializer):
    # UserProfile is related to User via OneToOneField
    public_key = serializers.CharField(source="userprofile.public_key", allow_null=True)

    class Meta:
        model = User
        fields = ["id", "username", "public_key"]


class UserPublicKeyUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ["public_key"]