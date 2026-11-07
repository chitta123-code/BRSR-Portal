from django.urls import path
from . import views

urlpatterns = [
    path(
        "",
        views.audit_trail_dashboard,
        name="audit_trail_dashboard",
    ),
]

