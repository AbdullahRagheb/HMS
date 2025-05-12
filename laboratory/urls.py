# laboratory/urls.py

from django.urls import path
from django.http import HttpResponse
from . import views

app_name = "laboratory"

def _todo(name):
    return lambda request, *args, **kwargs: HttpResponse(
        f"[{name}] view not implemented yet",
        content_type="text/plain"
    )

urlpatterns = [
    # 1) Test results list
    path("test-results/", _todo("test_results_list"), name="test_results_list"),
    path("test-results/<int:pk>/edit/", _todo("edit_test_result"), name="edit_test_result"),

    # 3) Test orders
    path("test-orders/add/", views.testorder_add, name="testorder_add"),
    path("test-orders/<int:pk>/update/", _todo("testorder_update"), name="testorder_update"),
    path("test-orders/<int:pk>/delete/", _todo("testorder_delete"), name="testorder_delete"),
    path("test-orders/<int:order_id>/add-result/", _todo("add_test_result"), name="add_test_result"),

    # 5) Print order
    path("test-orders/<int:pk>/print/", views.testorder_print, name="testorder_print"),

    # Sample QR
    path("samples/<int:sample_id>/barcode-print/", views.sample_barcode_print, name="sample_barcode_print"),
    path("samples/scan/<uuid:token>/", views.sample_scan, name="sample_scan"),

    # LabRequest workflow
    path("requests/add/", views.LabRequestCreateView.as_view(), name="lab_request_create"),
    path("requests/<int:pk>/", views.LabRequestDetailView.as_view(), name="lab_request_detail"),
    path("requests/scan/<uuid:token>/", views.lab_request_scan, name="lab_request_scan"),
]
