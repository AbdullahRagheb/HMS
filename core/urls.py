# core/urls.py

from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from django.shortcuts import redirect

urlpatterns = [
    # Redirect root → patient list
    path("", lambda request: redirect("manager:patient_list")),

    path("admin/", admin.site.urls),

    # built-in auth
    path("auth/", include("django.contrib.auth.urls")),

    # super-admin panel & login
    path("superadmin/", include(("superadmin.urls", "superadmin"), namespace="superadmin")),

    # hospital-manager module
    path("patients/", include(("manager.urls", "manager"), namespace="manager")),

    # HR module
    path("hr/", include(("hr.urls", "hr"), namespace="hr")),

    # staff self-service
    path("staff/", include(("staff.urls", "staff"), namespace="staff")),

    # misc shared views
    path("general/", include(("general.urls", "general"), namespace="general")),

    # laboratory namespace
    path("laboratory/", include(("laboratory.urls", "laboratory"), namespace="laboratory")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
