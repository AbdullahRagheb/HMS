from django.urls import path
from .views import (
    PatientListView, PatientDetailView, MedicalRecordCreateView,
    AppointmentCreateView
)

app_name = 'staff'

urlpatterns = [
    path('patients/', PatientListView.as_view(), name='patient_list'),
    path('patients/<int:pk>/', PatientDetailView.as_view(), name='patient_detail'),
    path('medical-records/create/', MedicalRecordCreateView.as_view(), name='medical_record_create'),
    path('appointments/new/', AppointmentCreateView.as_view(), name='appointment_create'),
]