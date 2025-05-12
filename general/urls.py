from django.urls import path
from .views import download_qr_code

app_name = 'general'

urlpatterns = [
    path('qr/<int:patient_id>/', download_qr_code, name='download_qr_code'),
]