from django.urls import path
from .views import GymLoginView, GymLogoutView, register

app_name = "accounts"

urlpatterns = [
    path("register/", register, name="register"),
    path("login/", GymLoginView.as_view(), name="login"),
    path("logout/", GymLogoutView.as_view(), name="logout"),
]
