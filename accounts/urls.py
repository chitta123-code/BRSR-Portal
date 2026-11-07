from django.urls import path
from django.contrib.auth import views as auth_views

from accounts.views import (
    portal_login,
    role_dashboard,
)


urlpatterns = [

    # Main BRSR / ESG portal login-selection page
    path(
        "",
        portal_login,
        name="portal_login"
    ),

    # Real Django authentication
    path(
        "login/",
        auth_views.LoginView.as_view(
            template_name="accounts/login.html",
            redirect_authenticated_user=True,
        ),
        name="login",
    ),

    # Role-based dashboard
    path(
        "dashboard/",
        role_dashboard,
        name="role_dashboard",
    ),

    # Logout
    path(
        "logout/",
        auth_views.LogoutView.as_view(),
        name="logout",
    ),
]

