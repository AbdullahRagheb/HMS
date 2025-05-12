# manager/urls.py
from django.urls import path
from .views import (
    
    # ── patient core ──────────────────────────────────────────────
    FluidBalanceCreateView, FormCreateView, ImmunizationCreateView, ObsToObsCreateView, PatientListView, PatientCreateView, PharmacyRequestDetailView, PharmacyRequestListView, PrescriptionDetailView, PrescriptionListView, PrescriptionRequestCreateView, ProcedureCreateView, ProgramCreateView, RadiologyOrderCreateView, dispense_action, patient_edit, PatientDetailView,
    download_patient_pdf, download_qr_code, download_wristband,
    # admissions
    AdmissionListView, AdmissionCreateView, discharge_admission, pharmacy_request_pdf_download, pharmacy_request_scan,
    transfer_create, admission_print, AdmissionPrintView, load_beds,
    # diagnosis / prescription
    DiagnosisCreateView, PrescriptionCreateView, FollowUpCreateView,
    # medical record
    medical_record_create, medical_record_print,
    # appointments & visits
    AppointmentListView, AppointmentCreateView, AppointmentUpdateView,
    AppointmentCancelView, VisitListView, VisitCreateView,
    # doctors
    DoctorListView, DoctorCreateView, DoctorUpdateView, DoctorDeleteView,
    DoctorDetailView,
    # beds & infrastructure
    BedListView, BedCreateView, BedUpdateView, BedDeleteView, BedDetailView,
    BuildingListView, BuildingCreateView, FloorListView, FloorCreateView,
    WardListView, WardCreateView, RoomListView, RoomCreateView,
    ajax_load_floors, ajax_load_wards, ajax_load_rooms,
    # departments & clinics
    department_list, department_page, department_doctors, department_patients,
    department_beds, department_rooms, add_department, department_detail,
    edit_department, delete_department, department_tree,
    clinic_list, clinic_create,
    # misc
    MedicationListView, MedicationCreateView,
    ObservationFormCreateView, pdf_settings,
    HRUserCreateView,
    EmergencyDepartmentCreateView, EmergencyDepartmentListView,
    SurgicalOperationsDepartmentCreateView, SurgicalOperationsDepartmentListView,
    icd11_autocomplete
)
from .views import VitalsCreateView
app_name = "manager"

urlpatterns = [
    # ── patients ────────────────────────────────────────────────
    path("", PatientListView.as_view(), name="patient_list"),
    path("create/", PatientCreateView.as_view(), name="patient_create"),
    path("<int:patient_id>/edit/", patient_edit, name="patient_edit"),
    path("<int:pk>/", PatientDetailView.as_view(), name="patient_detail"),

    # PDF / QR / wristband
    path("<int:patient_id>/pdf/",      download_patient_pdf, name="patient_pdf"),
    path("<int:patient_id>/wristband/",download_wristband,  name="download_wristband"),
    path("<int:patient_id>/qrcode/",   download_qr_code,    name="download_qr_code"),

    # ── admissions ──────────────────────────────────────────────
    path("admissions/", AdmissionListView.as_view(), name="admission_list"),
    path("admissions/new/", AdmissionCreateView.as_view(), name="new_admission"),
    path("admissions/<int:admission_id>/discharge/", discharge_admission, name="discharge_admission"),
    path("admissions/<int:admission_id>/transfer/",  transfer_create,     name="transfer_create"),
    path("admissions/<int:admission_id>/print/",     admission_print,     name="admission_print"),
    path("ajax/load-beds/", load_beds, name="ajax_load_beds"),

    # ── doctors ─────────────────────────────────────────────────
    path("doctors/",               DoctorListView.as_view(),   name="doctor_list"),
    path("doctors/add/",           DoctorCreateView.as_view(), name="doctor_add"),
    path("doctors/<int:pk>/edit/", DoctorUpdateView.as_view(), name="doctor_edit"),
    path("doctors/<int:pk>/delete/",DoctorDeleteView.as_view(),name="doctor_delete"),
    path("doctors/<int:pk>/",      DoctorDetailView.as_view(), name="doctor_detail"),

    # ── beds & infra ────────────────────────────────────────────
    path("beds/",            BedListView.as_view(),   name="bed_list"),
    path("beds/add/",        BedCreateView.as_view(), name="bed_add"),
    path("beds/<int:pk>/edit/",   BedUpdateView.as_view(), name="edit_bed"),
    path("beds/<int:pk>/delete/", BedDeleteView.as_view(), name="delete_bed"),
    path("beds/<int:pk>/",        BedDetailView.as_view(), name="bed_detail"),

    path("buildings/", BuildingListView.as_view(), name="building_list"),
    path("buildings/add/", BuildingCreateView.as_view(), name="building_add"),
    path("floors/", FloorListView.as_view(), name="floor_list"),
    path("floors/add/", FloorCreateView.as_view(), name="floor_add"),
    path("wards/", WardListView.as_view(), name="ward_list"),
    path("wards/add/", WardCreateView.as_view(), name="ward_add"),
    path("rooms/", RoomListView.as_view(), name="room_list"),
    path("rooms/add/", RoomCreateView.as_view(), name="room_add"),
    path("ajax/load-floors/", ajax_load_floors, name="ajax_load_floors"),
    path("ajax/load-wards/",  ajax_load_wards,  name="ajax_load_wards"),
    path("ajax/load-rooms/",  ajax_load_rooms,  name="ajax_load_rooms"),

    # ── departments / clinics ──────────────────────────────────
    path("departments/", department_list, name="department_list"),
    path("departments/add/", add_department, name="add_department"),
    path("departments/tree/", department_tree, name="department_tree"),
    path("departments/<int:department_id>/", department_page, name="department_page"),
    path("departments/<int:department_id>/doctors/",  department_doctors,  name="department_doctors"),
    path("departments/<int:department_id>/patients/", department_patients, name="department_patients"),
    path("departments/<int:department_id>/beds/",     department_beds,     name="department_beds"),
    path("departments/<int:department_id>/rooms/",    department_rooms,    name="department_rooms"),
    path("departments/<int:pk>/edit/",  edit_department,   name="edit_department"),
    path("departments/<int:pk>/delete/",delete_department, name="delete_department"),

    path("clinics/",         clinic_list,   name="clinic_list"),
    path("clinics/create/",  clinic_create, name="clinic_create"),

    # ── medical records ────────────────────────────────────────
    path("medical-records/create/", medical_record_create, name="medical_record_create"),
    path("medical-records/create/<int:patient_id>/", medical_record_create, name="medical_record_create_with_patient"),
    path("medical-records/print/",  medical_record_print,  name="medical_record_print"),

    # ── appointments / visits ──────────────────────────────────
    path("appointments/",             AppointmentListView.as_view(), name="appointment_list"),
    path("appointments/new/",         AppointmentCreateView.as_view(), name="appointment_create"),
    path("appointments/<int:pk>/edit/",  AppointmentUpdateView.as_view(), name="appointment_edit"),
    path("appointments/<int:pk>/cancel/",AppointmentCancelView.as_view(), name="appointment_cancel"),

    path("visits/",            VisitListView.as_view(), name="visit_list"),
    path("visits/new/",        VisitCreateView.as_view(), name="visit_create"),

    # diagnoses – two variants
    path("patients/diagnoses/new/", DiagnosisCreateView.as_view(), name="diagnosis_create"),  # ← NEW (patient only)
    path("visits/<int:visit_id>/diagnosis/new/", DiagnosisCreateView.as_view(), name="visit_diagnosis_create"),

    # prescriptions
    path("visits/<int:visit_id>/prescription/new/", PrescriptionCreateView.as_view(), name="prescription_create"),
    path("prescriptions/<int:prescription_id>/followup/new/", FollowUpCreateView.as_view(), name="followup_create"),
path(
    "patients/prescriptions/new/",
    PrescriptionCreateView.as_view(),
    name="prescription_create",          
),

path(
    "pharmacy/dispense/",
    dispense_action,
    name="dispense_action"
),

 path('pharmacy/prescriptions/', 
         PrescriptionListView.as_view(), 
         name='prescription_list'),
    path('pharmacy/prescriptions/new/',
         PrescriptionCreateView.as_view(),
         name='prescription_create'),
    path('pharmacy/prescriptions/<int:pk>/',
         PrescriptionDetailView.as_view(),
         name='prescription_detail'),
    path('pharmacy/dispense/',
         dispense_action,
         name='dispense_action'),


    # ── meds & misc ────────────────────────────────────────────
    path("medications/",      MedicationListView.as_view(), name="medication_list"),
    path("medications/new/",  MedicationCreateView.as_view(), name="medication_create"),

    path("create-observation/", ObservationFormCreateView.as_view(), name="create_observation"),
    path("pdf-settings/", pdf_settings, name="pdf_settings"),

    # ajax / autocomplete
    path("ajax/icd11-autocomplete/", icd11_autocomplete, name="icd11_autocomplete"),

    # HR
    path("hr-users/add/", HRUserCreateView.as_view(), name="hr_user_add"),

    path("fluid-balance/new/", FluidBalanceCreateView.as_view(), name="fluid_balance_create"),

    # ── vitals ───────────────────────────────────────────────
    path("vitals/new/", VitalsCreateView.as_view(), name="vitals_create"),

     path(
        "radiology-orders/new/",
        RadiologyOrderCreateView.as_view(),
        name="radiology_order_create",
    ),

path("create-observation/", ObservationFormCreateView.as_view(),
     name="create_observation"),
path("obstoobs/new/", ObservationFormCreateView.as_view(),
     name="obstoobs_create"),

     
path(
        "visits/<int:visit_id>/prescription/new/",
        PrescriptionCreateView.as_view(),
        name="visit_prescription_create",
    ),     

path(
    "immunizations/new/",
    ImmunizationCreateView.as_view(),          
    name="immunization_create",
),

path(
    "programs/new/",
    ProgramCreateView.as_view(),
    name="program_create",           
),

path(
    "forms/new/",
    FormCreateView.as_view(),
    name="form_create",          
),

path(
    'observation-form/create/',
    ObservationFormCreateView.as_view(),
    name='observation_form_create',   
),

path(
      'patients/obstoobs/new/',
      ObsToObsCreateView.as_view(),
      name='obstoobs_create'
    ),

path(
    'procedures/create/',
    ProcedureCreateView.as_view(),
    name='procedure_create',
),

path('requests/', PharmacyRequestListView.as_view(), name='pharmacy_request_list'),
    path('requests/new/', PrescriptionRequestCreateView.as_view(), name='pharmacy_request_new'),
    path('requests/<int:pk>/', PharmacyRequestDetailView.as_view(), name='pharmacy_request_detail'),
    path('requests/<int:pk>/pdf/', pharmacy_request_pdf_download, name='pharmacy_request_pdf'),
    path('requests/scan/<uuid:token>/', pharmacy_request_scan, name='pharmacy_request_scan'),
    # emergency & surgical departments
    path("emergency-department/",          EmergencyDepartmentListView.as_view(),          name="emergency_department_list"),
    path("emergency-department/create/",   EmergencyDepartmentCreateView.as_view(),        name="emergency_department_create"),
    path("surgical-operations-department/",SurgicalOperationsDepartmentListView.as_view(), name="surgical_operations_department_list"),
    path("surgical-operations-department/create/", SurgicalOperationsDepartmentCreateView.as_view(), name="surgical_operations_department_create"),
]

