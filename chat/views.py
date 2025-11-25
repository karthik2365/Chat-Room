import traceback
import sys
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from .models import UserProfile


from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login as auth_login, get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from rest_framework import generics, permissions, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes

from .models import UserProfile
from .serializers import (
    UserPublicSerializer,
    UserPublicKeyUpdateSerializer,
    UserPublicKeySerializer,
)


# GET /api/users/
class UserPublicListView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserPublicSerializer
    permission_classes = [permissions.IsAuthenticated]


# def home(request):
#     # simple landing page
#     return render(request, "home.html")


def register(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()          # creates auth.User -> visible in admin
            auth_login(request, user)   # log the user in
            return redirect("home")
    else:
        form = UserCreationForm()

    return render(request, "register.html", {"form": form})


@login_required
def chat_room(request, room_name):
    return render(request, "chat_room.html", {
        "room_name": room_name,
    })


@method_decorator(csrf_exempt, name="dispatch")
class MePublicKeyView(APIView):
    """
    POST /api/me/public-key/
    Body: { "public_key": "<base64-spki>" }
    Stores or updates the UserProfile.public_key for request.user
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        try:
            key = request.data.get("public_key")
            if not key:
                return Response({"detail": "public_key required"}, status=status.HTTP_400_BAD_REQUEST)

            profile, _ = UserProfile.objects.get_or_create(user=request.user)
            profile.public_key = key
            profile.save()
            return Response({"message": "Public key saved"})
        except Exception as exc:
            traceback.print_exc(file=sys.stderr)
            return Response({"detail": "Server error saving public key"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserPublicKeyView(APIView):
    """
    GET /api/users/<pk>/public-key/
    Returns { id, username, public_key }
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, pk, *args, **kwargs):
        user = get_object_or_404(User, pk=pk)
        try:
            profile = user.userprofile
            data = {
                "id": user.id,
                "username": user.username,
                "public_key": profile.public_key,
            }
        except UserProfile.DoesNotExist:
            data = {
                "id": user.id,
                "username": user.username,
                "public_key": None
            }
        return Response(data, status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes([IsAuthenticated])  # or AllowAny if you want it public
def user_public_key(request, pk):
    """
    GET /api/users/<pk>/public-key/  -> { "public_key": "<base64 spki>" }
    """
    # Use get_object_or_404 so we return 404 instead of 500
    profile = get_object_or_404(UserProfile, user__id=pk)
    return Response({"public_key": profile.public_key}, status=status.HTTP_200_OK)

class UserPublicKeyView(APIView):
    """
    GET /api/users/<id>/public-key/ → returns that user’s public key
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, user_id):
        try:
            profile = UserProfile.objects.get(user_id=user_id)
            ser = UserPublicKeySerializer(profile)
            return Response(ser.data)
        except UserProfile.DoesNotExist:
            return Response({"detail": "No public key found"}, status=404)


class MePublicKeyUpdateView(APIView):
    """
    POST /api/me/public-key/ → update logged-in user’s public key
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user
        try:
            profile = UserProfile.objects.get(user=user)
        except UserProfile.DoesNotExist:
            profile = UserProfile.objects.create(user=user)

        ser = UserPublicKeyUpdateSerializer(profile, data=request.data, partial=True)
        if ser.is_valid():
            ser.save()
            return Response({"status": "ok"})
        return Response(ser.errors, status=400)

def home(request):
    # If logged in, show their profile info (username + public key)
    if request.user.is_authenticated:
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        return render(request, "profile.html", {
            "username": request.user.username,
            "public_key": profile.public_key or "",
        })

    # Otherwise show login page
    form = AuthenticationForm(data=request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect("/")  # go back to home → profile
    return render(request, "registration/login.html", {"form": form})

@login_required
def profile(request):
    try:
        public_key = request.user.userprofile.public_key
    except UserProfile.DoesNotExist:
        public_key = None

    return render(request, "profile.html", {
        "username": request.user.username,
        "public_key": public_key,
    })

@login_required
def profile_view(request):
    return render(request, "profile.html", {"user": request.user})