from django.contrib.auth.models import User
from rest_framework import generics, permissions, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login as auth_login
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

from .models import UserProfile
from .serializers import (
    UserPublicSerializer,
    UserPublicKeyUpdateSerializer,
)


# GET /api/users/
class UserPublicListView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserPublicSerializer
    permission_classes = [permissions.IsAuthenticated]


# POST /api/me/public-key/
class MePublicKeyView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        serializer = UserPublicKeyUpdateSerializer(
            instance=profile, data=request.data, partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

def home(request):
    # simple landing page
    return render(request, "home.html")


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

from django.contrib.auth.decorators import login_required

@login_required
def chat_room(request, room_name):
    return render(request, "chat_room.html", {
        "room_name": room_name,
    })

from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

@method_decorator(csrf_exempt, name="dispatch")
class MePublicKeyView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        try:
            public_key = request.data.get("public_key")
            if not public_key:
                return Response({"detail": "public_key is required"}, status=status.HTTP_400_BAD_REQUEST)

            profile, _ = UserProfile.objects.get_or_create(user=request.user)
            profile.public_key = public_key
            profile.save()

            return Response({"message": "Public key saved"})
        except Exception as exc:
            # always log the exception so you can inspect server console
            import traceback, sys
            traceback.print_exc(file=sys.stderr)
            return Response({"detail": "Server error saving public key"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
User = get_user_model()

class UserPublicKeyView(APIView):
    """
    GET /api/users/<pk>/public-key/
    Returns: { id, username, public_key } or 404
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, pk, *args, **kwargs):
        user = get_object_or_404(User, pk=pk)
        # If you store public_key on a related UserProfile:
        try:
            profile = user.userprofile  # adjust if relation name differs
            public_key = profile.public_key
        except Exception:
            public_key = None

        return Response({
            "id": user.id,
            "username": user.username,
            "public_key": public_key
        }, status=status.HTTP_200_OK)