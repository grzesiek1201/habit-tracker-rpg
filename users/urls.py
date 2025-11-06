from django.urls import path

from .views import (
    UserCreateView,
    LoginView,
    RefreshView,
    LogoutView,
    MeView,
    ProfileUpdateView,
    ChangePasswordView,
)

urlpatterns = [
    # --- Authentication & Token Management ---
    path("register/", UserCreateView.as_view(), name="user-register"),         # User registration
    path("login/", LoginView.as_view(), name="token-obtain-pair"),            # Obtain JWT access and refresh tokens
    path("refresh/", RefreshView.as_view(), name="token-refresh"),            # Refresh JWT access token
    path("logout/", LogoutView.as_view(), name="token-logout"),               # Logout (blacklist refresh token)

    # --- User Profile Management ---
    path("profile/", MeView.as_view(), name="user-me"),                       # Get current user data
    path("profile/update/", ProfileUpdateView.as_view(), name="user-update"), # Update email or avatar
    path("profile/change-password/", ChangePasswordView.as_view(), name="change-password"), # Change user password
]
