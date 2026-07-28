from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import redirect, render

from .forms import RegistrationForm


def register(request):
    if request.user.is_authenticated:
        return redirect("resources:list")
    form = RegistrationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, "Welcome to GymFlow.")
        return redirect("resources:list")
    return render(request, "accounts/register.html", {"form": form})


class GymLoginView(LoginView):
    template_name = "accounts/login.html"


class GymLogoutView(LogoutView):
    pass
