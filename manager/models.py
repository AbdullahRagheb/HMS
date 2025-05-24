from datetime import date, datetime
from io import BytesIO
import uuid
from django.core.files.base import ContentFile
from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from mptt.models import MPTTModel, TreeForeignKey
import qrcode


# ────────────────────────  ORGANISATION & STAFF  ────────────────────────
class Department(MPTTModel):
    TYPE_CHOICES = [
        ('unit', 'Unit'),
        ('department', 'Department'),
        ('administration', 'Administration'),
        ('medical', 'Medical Department'),
        ('emergency', 'Emergency'),
        ('surgical', 'Surgical Operations'),
    ]
    name = models.CharField(max_length=100, unique=True)
    parent = TreeForeignKey(
        'self', on_delete=models.CASCADE, null=True, blank=True, related_name='children'
    )
    department_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='department')
    hospital = models.ForeignKey('superadmin.Hospital', on_delete=models.CASCADE, related_name='departments')
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    class MPTTMeta:
        order_insertion_by = ['name']

    def __str__(self):
        return f"{self.name} – {self.hospital.name}"


class Doctor(models.Model):
    user = models.OneToOneField(
        'hr.CustomUser', on_delete=models.CASCADE, limit_choices_to={'role': 'doctor'}
    )
    departments = models.ManyToManyField(Department, related_name='doctors')

    def __str__(self):
        return f"{self.user.full_name} (Doctor)"


# ───────────────────────────  INFRASTRUCTURE  ───────────────────────────
class Building(models.Model):
    name = models.CharField(max_length=100)
    hospital = models.ForeignKey('superadmin.Hospital', on_delete=models.CASCADE, related_name='buildings')
    location = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return self.name


class Floor(models.Model):
    name = models.CharField(max_length=50)
    building = models.ForeignKey(Building, on_delete=models.CASCADE, related_name='floors')
    floor_number = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.name} – {self.building.name}"


class Ward(models.Model):
    name = models.CharField(max_length=100)
    floor = models.ForeignKey(Floor, on_delete=models.CASCADE, related_name='wards')
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.name} – {self.floor.name}"


class Room(models.Model):
    number = models.CharField(max_length=50)
    ward = models.ForeignKey(Ward, on_delete=models.CASCADE, related_name='rooms')
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='rooms')
    capacity = models.IntegerField(default=1)

    def __str__(self):
        return f"Room {self.number} – {self.ward.name}"


class Bed(models.Model):
    BED_TYPE_CHOICES = [
        ('regular', 'سرير عادي'),
        ('icu', 'سرير عناية مركزة'),
        ('nicu', 'حضانة أطفال'),
        ('clinic_office', 'مكتب في العيادة الخارجية'),
        ('er_office', 'مكتب في عيادة الإسعاف'),
    ]
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('occupied', 'مستخدم'),
        ('maintenance', 'تحت الصيانة'),
        ('cleaning', 'قيد التنظيف'),
    ]
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='beds')
    bed_number = models.CharField(max_length=10)
    bed_type = models.CharField(max_length=20, choices=BED_TYPE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')

    def __str__(self):
        return f"{self.get_bed_type_display()} – {self.room} (Bed {self.bed_number})"

    @property
    def building(self):
        return self.room.ward.floor.building

    @property
    def floor(self):
        return self.room.ward.floor

    @property
    def ward(self):
        return self.room.ward

    @property
    def department(self):
        return self.room.department


# ─────────────────────────────  PATIENT  ─────────────────────────────
class Patient(models.Model):
    first_name = models.CharField(max_length=50)
    middle_name = models.CharField(max_length=50, blank=True, null=True)
    last_name = models.CharField(max_length=50)
    birth_year = models.IntegerField(null=True, blank=True)
    birth_month = models.IntegerField(null=True, blank=True)
    birth_day = models.IntegerField(null=True, blank=True)
    birth_hour = models.TimeField(null=True, blank=True)
    death_hour = models.TimeField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')])
    address = models.TextField()
    hospital = models.ForeignKey('superadmin.Hospital', on_delete=models.CASCADE, null=True, blank=True)
    phone_number = models.CharField(max_length=20)
    whatsapp_number = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    occupation = models.CharField(max_length=50, blank=True, null=True)
    religion = models.CharField(max_length=50, blank=True, null=True)
    place_of_birth = models.CharField(max_length=100, blank=True, null=True)
    mrn = models.CharField(max_length=20, unique=True, blank=True)
    medical_file_number = models.CharField(max_length=20, unique=True, blank=True)
    national_id = models.CharField(max_length=20, unique=True)
    photo = models.ImageField(upload_to='patient_photos/', blank=True, null=True)
    passport = models.ImageField(upload_to='id_documents/', blank=True, null=True)
    id_card = models.ImageField(upload_to='id_documents/', blank=True, null=True)
    companion_name = models.CharField(max_length=100, blank=True, null=True)
    companion_phone = models.CharField(max_length=20, blank=True, null=True)
    companion_relationship = models.CharField(
        max_length=20,
        choices=[
            ('Parent', 'Parent'),
            ('Spouse', 'Spouse'),
            ('Child', 'Child'),
            ('Sibling', 'Sibling'),
            ('Friend', 'Friend'),
            ('Other', 'Other'),
        ],
        blank=True,
        null=True,
    )

    def __str__(self):
        return f"{self.first_name} {self.last_name} (MRN {self.mrn})"

    # calculated properties
    @property
    def full_name(self):
        if self.middle_name:
            return f"{self.first_name} {self.middle_name} {self.last_name}"
        return f"{self.first_name} {self.last_name}"
        
    @property
    def date_of_birth(self):
        if self.birth_year and self.birth_month and self.birth_day:
            if self.birth_hour:
                return datetime(
                    self.birth_year, self.birth_month, self.birth_day,
                    self.birth_hour.hour, self.birth_hour.minute, self.birth_hour.second
                )
            return date(self.birth_year, self.birth_month, self.birth_day)
        return None

    @property
    def age(self):
        dob = self.date_of_birth
        if not dob:
            return {'years': 0, 'months': 0, 'days': 0}
        today = datetime.now() if isinstance(dob, datetime) else date.today()
        delta = today - dob
        years = delta.days // 365
        months = (delta.days % 365) // 30
        days = (delta.days % 365) % 30
        return {'years': years, 'months': months, 'days': days}

    @property
    def age_category(self):
        years = self.age['years']
        if years < 1:
            return 'newborn'
        elif years < 18:
            return 'pediatric'
        return 'adult'

    def save(self, *args, **kwargs):
        if not self.mrn:
            next_num = self.pk or Patient.objects.count() + 1
            self.mrn = f"MRN-{next_num:06d}"
        if not self.medical_file_number:
            self.medical_file_number = self.mrn
        super().save(*args, **kwargs)

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=models.Q(passport__isnull=False) | models.Q(id_card__isnull=False),
                name='patient_identification_document_provided',
            )
        ]


# ────────────────────────  RADIOLOGY ORDER  ────────────────────────
class RadiologyOrder(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    order_date = models.DateTimeField(auto_now_add=True)
    radiology_type = models.CharField(max_length=50)
    status = models.CharField(max_length=20, default='Pending')

    def __str__(self):
        return f"{self.radiology_type} – {self.patient}"


# ────────────────────────  MEDICAL RECORD  ────────────────────────
class MedicalRecord(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    complaint = models.TextField()
    medical_history = models.TextField(blank=True, null=True)
    surgical_history = models.TextField(blank=True, null=True)
    medication_history = models.TextField(blank=True, null=True)
    family_history = models.TextField(blank=True, null=True)
    allergies = models.TextField(blank=True, null=True)
    clinical_examination = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Basic info
    name = models.CharField(max_length=100, blank=True, null=True)
    dob = models.DateField(blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, null=True)
    mrn = models.CharField(max_length=50, blank=True, null=True)
    weight = models.FloatField(blank=True, null=True)
    height = models.FloatField(blank=True, null=True)
    bmi = models.FloatField(blank=True, null=True)

    # admission + history JSON fields
    source_history = models.JSONField(blank=True, null=True)
    present_at_bedside = models.JSONField(blank=True, null=True)
    referral_source = models.JSONField(blank=True, null=True)
    history_limitation = models.JSONField(blank=True, null=True)

    past_medical_history = models.TextField(blank=True, null=True)
    allergic_history = models.TextField(blank=True, null=True)
    social_history = models.TextField(blank=True, null=True)
    past_surgical_history = models.TextField(blank=True, null=True)
    immunization_history = models.TextField(blank=True, null=True)
    nutritional_history = models.TextField(blank=True, null=True)
    psychiatric_history = models.TextField(blank=True, null=True)

    # SOAP / HPI JSON
    hpi = models.JSONField(blank=True, null=True)
    ros = models.JSONField(blank=True, null=True)
    physical_exam = models.JSONField(blank=True, null=True)
    medical_decision = models.JSONField(blank=True, null=True)
    interpretation = models.JSONField(blank=True, null=True)
    impression_plan = models.JSONField(blank=True, null=True)

    professional_service = models.TextField(blank=True, null=True)
    patient_education = models.TextField(blank=True, null=True)
    soap_note = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Medical Record – {self.patient} ({self.created_at:%Y-%m-%d})"


# ───────────────────────────  ADMISSION  ───────────────────────────
class Admission(models.Model):
    TYPE_CHOICES = [('emergency', 'Emergency'), ('regular', 'Regular'), ('surgical', 'Surgical')]
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    admission_date = models.DateTimeField(auto_now_add=True)
    admission_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    treating_doctor = models.ForeignKey(Doctor, on_delete=models.SET_NULL, null=True)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True)
    bed = models.ForeignKey(Bed, on_delete=models.SET_NULL, null=True)
    reason_for_admission = models.TextField(blank=True, null=True)
    insurance_info = models.CharField(max_length=100, blank=True, null=True)
    discharge_date = models.DateTimeField(blank=True, null=True)
    discharge_report = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Admission – {self.patient} ({self.admission_date:%Y-%m-%d})"


class Transfer(models.Model):
    TYPE_CHOICES = [('internal', 'Internal'), ('external', 'External')]
    admission = models.ForeignKey(Admission, on_delete=models.CASCADE)
    transfer_date = models.DateTimeField(auto_now_add=True)
    transfer_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    from_department = models.ForeignKey(Department, related_name='transfers_from', on_delete=models.SET_NULL, null=True)
    to_department = models.ForeignKey(Department, related_name='transfers_to', on_delete=models.SET_NULL, null=True, blank=True)
    to_hospital = models.CharField(max_length=100, blank=True, null=True)
    transfer_file = models.TextField(blank=True, null=True)
    new_bed = models.ForeignKey(Bed, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"Transfer – {self.admission.patient} ({self.transfer_type})"


# ─────────────────────────  CLINIC & APPOINTMENT  ─────────────────────────
class Clinic(models.Model):
    TYPE_CHOICES = [('department', 'Department'), ('physician', 'Physician')]
    name = models.CharField(max_length=100)
    clinic_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)
    doctor = models.ForeignKey(Doctor, on_delete=models.SET_NULL, null=True, blank=True)
    hospital = models.ForeignKey('superadmin.Hospital', on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.name


class Appointment(models.Model):
    STATUS_CHOICES = [
        ('Scheduled', 'Scheduled'),
        ('Completed', 'Completed'),
        ('Canceled', 'Canceled'),
        ('Rescheduled', 'Rescheduled'),
        ('No Show', 'No Show'),
    ]
    TYPE_CHOICES = [
        ('outpatient', 'Outpatient Clinic'),
        ('inpatient', 'Inpatient Clinic'),
        ('emergency', 'Emergency Room'),
        ('surgery', 'Surgery'),
    ]
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    clinic = models.ForeignKey(Clinic, on_delete=models.CASCADE)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)
    doctor = models.ForeignKey(Doctor, on_delete=models.SET_NULL, null=True, blank=True)
    date_time = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Scheduled')
    appointment_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='outpatient')
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.patient} – {self.appointment_type} @ {self.date_time:%Y-%m-%d %H:%M}"


# ───────────────────────────────  VISIT  ───────────────────────────────
class Visit(models.Model):
    VISIT_TYPES = [('outpatient', 'Outpatient Clinic'), ('inpatient', 'Inpatient Clinic'), ('surgery', 'Surgery')]
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.SET_NULL, null=True)
    visit_type = models.CharField(max_length=20, choices=VISIT_TYPES)
    visit_date = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.patient} – {self.visit_type} ({self.visit_date:%Y-%m-%d})"


# ───────────────────────  EMERGENCY / SURGICAL DEPTS  ───────────────────────
class EmergencyDepartment(models.Model):
    STATUS_CHOICES = [('active', 'Active'), ('inactive', 'Inactive'), ('maintenance', 'Under Maintenance')]
    name = models.CharField(max_length=100)
    hospital = models.ForeignKey('superadmin.Hospital', on_delete=models.CASCADE)
    emergency_type = models.CharField(max_length=50)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)
    doctor = models.ForeignKey(Doctor, on_delete=models.SET_NULL, null=True, blank=True)
    location = models.CharField(max_length=100, blank=True)
    capacity = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Emergency Department"
    def __str__(self):
        return f"{self.name} ({self.emergency_type})"


class SurgicalOperationsDepartment(models.Model):
    STATUS_CHOICES = [('active', 'Active'), ('inactive', 'Inactive'), ('maintenance', 'Under Maintenance')]
    name = models.CharField(max_length=100)
    hospital = models.ForeignKey('superadmin.Hospital', on_delete=models.CASCADE)
    surgical_type = models.CharField(max_length=50)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)
    doctor = models.ForeignKey(Doctor, on_delete=models.SET_NULL, null=True, blank=True)
    location = models.CharField(max_length=100, blank=True)
    operating_rooms = models.PositiveIntegerField(default=1)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Surgical Operations Department"
    def __str__(self):
        return f"{self.name} ({self.surgical_type})"


# ─────────────────────────────  DIAGNOSIS  ─────────────────────────────
class Diagnosis(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    visit = models.ForeignKey(Visit, on_delete=models.CASCADE, null=True, blank=True)
    doctor = models.ForeignKey(Doctor, on_delete=models.SET_NULL, null=True)
    icd_code = models.CharField(max_length=10, verbose_name=_("ICD Code"))
    name = models.CharField(max_length=255, verbose_name=_("Diagnosis Title"))
    description = models.TextField(blank=True, null=True, verbose_name=_("Description"))
    inclusions = models.TextField(blank=True, null=True)
    exclusions = models.TextField(blank=True, null=True)
    foundation_uri = models.URLField(blank=True, null=True)
    index_terms = models.TextField(blank=True, null=True)
    coded_elsewhere = models.TextField(blank=True, null=True)
    related_maternal_codes = models.TextField(blank=True, null=True)
    related_perinatal_codes = models.TextField(blank=True, null=True)
    postcoordination_options = models.TextField(blank=True, null=True)
    additional_notes = models.TextField(blank=True, null=True)
    external_reference_link = models.URLField(blank=True, null=True)
    icd_chapter = models.CharField(max_length=100, blank=True, null=True)
    date_diagnosed = models.DateTimeField(auto_now_add=True)
    internal_notes = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = _("Diagnosis")
        verbose_name_plural = _("Diagnoses")

    def __str__(self):
        return f"{self.name} ({self.icd_code}) – {self.patient}"


# ──────────────────────────  BACTERIOLOGY  ──────────────────────────
class BacteriologyResult(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    test_date = models.DateTimeField(default=timezone.now)
    sample_type = models.CharField(max_length=100)
    result = models.TextField()
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Bacteriology #{self.pk} – {self.patient}"


# ───────────────────────────  PROGRAM & FORM  ───────────────────────────
class Program(models.Model):
    patient     = models.ForeignKey(
        Patient, on_delete=models.CASCADE, related_name="programs"
    )
    name        = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    # (optional) add extra fields you already show in the template
    start_date  = models.DateField(null=True, blank=True)
    status      = models.CharField(max_length=50, blank=True)


class Form(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    form_type = models.CharField(max_length=100)
    filled_by = models.CharField(max_length=100, blank=True, null=True)
    date_filled = models.DateTimeField(default=timezone.now)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.form_type} – {self.patient}"


# ───────────────────────────────  LAB  ───────────────────────────────
class Laboratory(models.Model):
    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    contact_number = models.CharField(max_length=15, blank=True, null=True)
    email = models.EmailField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.name


class TestOrder(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    test_name = models.CharField(max_length=255)
    order_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50)

    def __str__(self):
        return self.test_name


class Sample(models.Model):
    test_order = models.ForeignKey(TestOrder, on_delete=models.CASCADE, related_name='samples')
    sample_type = models.CharField(max_length=100)

    def __str__(self):
        return self.sample_type


class TestResult(models.Model):
    test_order = models.ForeignKey(TestOrder, on_delete=models.CASCADE, related_name='results')
    result = models.CharField(max_length=100)

    def __str__(self):
        return self.result


# ─────────────────────────────  OBSERVATION  ─────────────────────────────
class Observation(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    hospital = models.ForeignKey('superadmin.Hospital', on_delete=models.CASCADE)
    note = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Observation – {self.patient} @ {self.timestamp:%Y-%m-%d}"


# ──────────────────────────────  PROCEDURE  ──────────────────────────────
class Procedure(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    code = models.CharField(max_length=20, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


# ───────────────────────────────  PACS  ───────────────────────────────
class PACS(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    study_date = models.DateTimeField(default=timezone.now)
    study_type = models.CharField(max_length=100)
    image_url = models.URLField(blank=True, null=True)
    report = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"PACS {self.pk} – {self.patient}"


# ─────────────────────────────  MEDICATION  ─────────────────────────────
class Medication(models.Model):
    name           = models.CharField(max_length=200)
    form           = models.CharField(max_length=100)
    quantity       = models.PositiveIntegerField()
    price          = models.DecimalField(max_digits=8, decimal_places=2)
    barcode        = models.CharField(max_length=64, unique=True, null=True, blank=True)

    # NEW: a default dosage string your JS can auto-insert
    default_dosage = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Suggested dosage to auto-populate"
    )

    def __str__(self):
        return self.name


class Prescription(models.Model):
    patient          = models.ForeignKey('Patient', on_delete=models.CASCADE)
    medication       = models.ForeignKey('Medication', on_delete=models.PROTECT)
    dosage           = models.CharField(max_length=100)

    ROUTE_CHOICES = [
        ('oral', 'Oral'),
        ('iv',   'Intravenous'),
        ('im',   'Intramuscular'),
    ]
    # nullable so existing records pass through
    route            = models.CharField(
                          max_length=20,
                          choices=ROUTE_CHOICES,
                          default='oral',
                          null=True,
                          blank=True,
                      )
    number_of_doses  = models.PositiveIntegerField(null=True, blank=True)
    total_dose       = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    first_dose_date  = models.DateField(null=True, blank=True)
    instructions     = models.TextField(null=True, blank=True)
    doctor           = models.ForeignKey(
                          settings.AUTH_USER_MODEL,
                          on_delete=models.SET_NULL,
                          null=True,
                          blank=True
                      )
    # use default=timezone.now instead of auto_now_add so migrations can backfill
    date_prescribed  = models.DateField(default=timezone.now)

    def __str__(self):
        return f"{self.medication.name} for {self.patient}"

class DispenseRecord(models.Model):
    ACTIONS = [
      ("prepared",    "Prepared by pharmacy"),
      ("dispensed",   "Handed to nurse"),
      ("administered","Given to patient"),
    ]

    prescription            = models.ForeignKey(
                                Prescription,
                                on_delete=models.CASCADE,
                                related_name="dispense_history"
                              )
    action                  = models.CharField(max_length=20,
                                               choices=ACTIONS)
    performed_by            = models.ForeignKey(
                                settings.AUTH_USER_MODEL,
                                on_delete=models.PROTECT
                              )
    performed_at            = models.DateTimeField(auto_now_add=True)
    patient_barcode_scanned = models.BooleanField(
                                default=False,
                                help_text="True once patient wristband scanned"
                              )
    medication_barcode_scanned = models.BooleanField(
                                  default=False,
                                  help_text="True once med barcode scanned"
                                )

    class Meta:
        ordering = ("-performed_at",)

    def __str__(self):
        return f"{self.get_action_display()} @ {self.performed_at:%Y-%m-%d %H:%M}"

class FollowUp(models.Model):
    prescription = models.ForeignKey(Prescription, on_delete=models.CASCADE, related_name='followups')
    follow_up_date = models.DateTimeField()
    notes = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('completed', 'Completed')], default='pending')

    def __str__(self):
        return f"Follow-up {self.pk} – {self.prescription}"


# ───────────────────────────  PDF SETTINGS  ───────────────────────────
class PDFSettings(models.Model):
    """
    Settings for PDF generation, stored per-hospital.
    """
    hospital = models.OneToOneField(
        'superadmin.Hospital',
        on_delete=models.CASCADE,
        related_name='pdf_settings'
    )
    
    # Header and footer
    header_text = models.CharField(max_length=255, blank=True, null=True)
    header_image = models.ImageField(upload_to='pdf_headers/', blank=True, null=True)
    footer_text = models.CharField(max_length=255, blank=True, null=True)
    
    # Style settings
    font_size = models.IntegerField(default=10)
    table_border_color = models.CharField(max_length=20, default='grey')
    
    # Content toggles for patient PDF
    include_hospital_logo = models.BooleanField(default=True)
    include_patient_details = models.BooleanField(default=True)
    include_medical_records = models.BooleanField(default=True)
    include_companion_info = models.BooleanField(default=True)
    
    # Medical record section toggles
    include_basic_info = models.BooleanField(default=True)
    include_complaint = models.BooleanField(default=True)
    include_allergies = models.BooleanField(default=True)
    include_medical_history = models.BooleanField(default=True)
    include_physical_exam = models.BooleanField(default=True)
    include_diagnosis = models.BooleanField(default=True)
    
    def __str__(self):
        return f"PDF Settings for {self.hospital.name}"

class Immunization(models.Model):
    patient   = models.ForeignKey(Patient, on_delete=models.CASCADE)
    vaccine   = models.CharField(max_length=100)
    date_given= models.DateField()
    notes     = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.vaccine} – {self.patient}"
    
class ObsToObs(models.Model):
    patient     = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name='obstoobs_forms'
    )
    name        = models.CharField(max_length=255)
    created_at  = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} for {self.patient}"
    
class VitalSign(models.Model):
    """
    Stores structured vital signs linked to a medical record.
    """
    medical_record = models.ForeignKey(
        'MedicalRecord',
        on_delete=models.CASCADE,
        related_name='vitals'
    )
    taken_at = models.DateTimeField(default=timezone.now)
    temperature = models.DecimalField(
        max_digits=4, decimal_places=1,
        help_text="Body temperature in °C"
    )
    heart_rate = models.PositiveSmallIntegerField(
        help_text="Heart rate in beats per minute"
    )
    respiratory_rate = models.PositiveSmallIntegerField(
        help_text="Respiratory rate in breaths per minute"
    )
    systolic_bp = models.PositiveSmallIntegerField(
        help_text="Systolic blood pressure (mmHg)"
    )
    diastolic_bp = models.PositiveSmallIntegerField(
        help_text="Diastolic blood pressure (mmHg)"
    )
    oxygen_saturation = models.PositiveSmallIntegerField(
        help_text="Oxygen saturation (%)"
    )

    class Meta:
        ordering = ['-taken_at']

    def __str__(self):
        return f"Vitals at {self.taken_at:%Y-%m-%d %H:%M}"

class FluidBalance(models.Model):
    """
    Tracks daily fluid intake and output for body-fluid calculations.
    """
    medical_record = models.ForeignKey(
        'MedicalRecord',
        on_delete=models.CASCADE,
        related_name='fluid_balances'
    )
    recorded_at = models.DateTimeField(default=timezone.now)
    intake_ml = models.FloatField(
        help_text="Total fluid intake in milliliters"
    )
    output_ml = models.FloatField(
        help_text="Total fluid output in milliliters"
    )

    class Meta:
        ordering = ['-recorded_at']

    @property
    def net_balance(self):
        """Return net fluid (intake minus output) in mL."""
        return self.intake_ml - self.output_ml

    def __str__(self):
        return (f"Fluid {self.recorded_at:%Y-%m-%d %H:%M}: "
                f"in {self.intake_ml}ml, out {self.output_ml}ml")

class PharmacyRequest(models.Model):
    STATUS_SUBMITTED = 'submitted'
    STATUS_ACCEPTED  = 'accepted'
    STATUS_READY     = 'ready'
    STATUS_DISPENSED = 'dispensed'
    STATUS_CHOICES = [
        (STATUS_SUBMITTED, 'Submitted'),
        (STATUS_ACCEPTED,  'Accepted'),
        (STATUS_READY,     'Ready'),
        (STATUS_DISPENSED, 'Dispensed'),
    ]

    patient       = models.ForeignKey('manager.Patient',    on_delete=models.CASCADE)
    prescription  = models.ForeignKey('manager.Prescription', on_delete=models.CASCADE)
    status        = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_SUBMITTED)
    token         = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    qr_code       = models.ImageField(upload_to='pharmacy_qrcodes/', blank=True)
    created_at    = models.DateTimeField(auto_now_add=True)

    def get_scan_url(self):
        return reverse('manager:pharmacy_request_scan', args=[str(self.token)])

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # generate QR
        url = self.get_scan_url()
        img = qrcode.make(url)
        buf = BytesIO()
        img.save(buf, format='PNG')
        self.qr_code.save(f"{self.token}.png", ContentFile(buf.getvalue()), save=False)
        super().save(update_fields=['qr_code'])

class PrescriptionRequest(models.Model):
    STATUS_SUBMITTED = 'submitted'
    STATUS_ACCEPTED  = 'accepted'
    STATUS_READY     = 'ready'
    STATUS_DISPENSED = 'dispensed'
    STATUS_CHOICES = [
        (STATUS_SUBMITTED, 'Submitted'),
        (STATUS_ACCEPTED, 'Accepted'),
        (STATUS_READY, 'Ready'),
        (STATUS_DISPENSED, 'Dispensed'),
    ]

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='prescription_requests')
    create_pharmacy_request = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_SUBMITTED)
    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    qr_code = models.ImageField(upload_to='pharmacy_request_qrcodes/', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def get_scan_url(self):
        return reverse('manager:pharmacy_request_scan', args=[str(self.token)])

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.create_pharmacy_request and not self.qr_code:
            url = self.get_scan_url()
            img = qrcode.make(url)
            buf = BytesIO()
            img.save(buf, format='PNG')
            self.qr_code.save(f"{self.token}.png", ContentFile(buf.getvalue()), save=False)
            super().save(update_fields=['qr_code'])

class PrescriptionRequestItem(models.Model):
    request = models.ForeignKey(PrescriptionRequest, on_delete=models.CASCADE, related_name='items')
    medication = models.ForeignKey(Medication, on_delete=models.PROTECT)
    dosage = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.medication.name}: {self.dosage}"
