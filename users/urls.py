from django.urls import path
from .views import ChangePasswordView, LogoutView, MeView, ProfileUpdateView, UserCreateView, LoginView, RefreshView


urlpatterns = [
    path("register/", UserCreateView.as_view(), name="user-register"),
    path("login/", LoginView.as_view(), name="token_obtain_pair"),
    path("refresh/", RefreshView.as_view(), name="token_refresh"),
    path("logout/", LogoutView.as_view(), name="token_logout"),

    path("profile/", MeView.as_view(), name="user-me"),
    path("profile/update/", ProfileUpdateView.as_view(), name="user-update"),
    path("profile/change-password/", ChangePasswordView.as_view(), name="change-password"),
]
