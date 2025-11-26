"""
URL configuration for securechat_backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from chat.views import home, register, user_public_key, MePublicKeyView, MePublicKeyUpdateView, UserPublicListView, chat_room, UserPublicKeyView, profile_view


urlpatterns = [
    path("admin/", admin.site.urls),
    path("", home, name="home"),
    path("register/", register, name="register"),
    path("profile/", profile_view, name="profile"),
    
    # built-in auth views: /login/, /logout/, /password_change/, etc.
    path("accounts/", include("django.contrib.auth.urls")),
    path("chat/<str:room_name>/", chat_room, name="chat_room"),

    path('api/users/', UserPublicListView.as_view()),
    path("api/me/public-key/", MePublicKeyView.as_view(), name="me-public-key"),
    path("api/users/<int:pk>/public-key/", UserPublicKeyView.as_view(), name="user-public-key"),
]
