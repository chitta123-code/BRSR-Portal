"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.1/topics/http/urls/
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

from brsr import views
from config.views import home
from django.contrib import admin
from django.urls import path, include
from django.shortcuts import render
from django.conf import settings
from django.conf.urls.static import static


# Keep your existing imports for these views
# from reporting.views import brsr_entry, reviewer_dashboard, review_submission


urlpatterns = [

    path("", home, name="home"),

    path("", include("reporting.urls")),

    path("admin/", admin.site.urls),

    path("accounts/", include("accounts.urls")),

    path( "ingestion/",include("ingestion.urls")),

    path("esg/", include("esg_data.urls")),

    path("audit-trail/", include("audit_trail.urls")),


]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )
