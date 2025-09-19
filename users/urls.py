from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import ChangePasswordView, LogoutView, MeView, ProfileUpdateView, UserCreateView   


urlpatterns = [
    path("register/", UserCreateView.as_view(), name="user-register"),
    path("login/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("logout/", LogoutView.as_view(), name="token_logout"),

    path("me/", MeView.as_view(), name="user-me"),
    path("me/update/", ProfileUpdateView.as_view(), name="user-update"),
    path("me/change-password/", ChangePasswordView.as_view(), name="change-password"),
]
