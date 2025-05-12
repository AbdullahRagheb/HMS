from django.urls import path
from .views import (
    CustomLoginView, CustomLogoutView, UserListView, UserCreateView,
    UserUpdateView, UserDeleteView, HospitalCreateView, HospitalListView,
    SuperAdminSystemSettingsUpdateView
)

app_name = 'superadmin'  # Namespace for superadmin URLs

urlpatterns = [
    # Authentication URLs
    path('accounts/login/', CustomLoginView.as_view(), name='login'),
    path('accounts/logout/', CustomLogoutView.as_view(), name='logout'),

    # User Management URLs
    path('users/', UserListView.as_view(), name='user_list'),
    path('users/create/', UserCreateView.as_view(), name='user_create'),
    path('users/<int:pk>/update/', UserUpdateView.as_view(), name='user_update'),
    path('users/<int:pk>/delete/', UserDeleteView.as_view(), name='user_delete'),

    # Hospital Management URLs
    path('create-hospital/', HospitalCreateView.as_view(), name='create_hospital'),
    path('hospitals/', HospitalListView.as_view(), name='hospital_list'),

    # System Settings URL
    path('system-settings/superadmin/', SuperAdminSystemSettingsUpdateView.as_view(), name='system_settings'),
]