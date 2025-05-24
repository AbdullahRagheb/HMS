from datetime import date, datetime
import logging

from django import forms
from django.core.exceptions import ValidationError

from .models import (
    Admission, Appointment, BacteriologyResult, Bed, Building, Clinic, Department,
    Diagnosis, DispenseRecord, Doctor, EmergencyDepartment, Floor, FluidBalance, FollowUp, Form, Immunization, MedicalRecord,
    Medication, ObsToObs, Observation, PACS, Patient, Prescription, PrescriptionRequest, PrescriptionRequestItem, Program, RadiologyOrder,
    Room, SurgicalOperationsDepartment, Transfer, Visit, VitalSign, Ward, PDFSettings,
    Procedure                         
)
from superadmin.models import Hospital
from hr.models import CustomUser

# Existing forms (unchanged)
class AdmissionForm(forms.ModelForm):
    class Meta:
        model = Admission
        fields = [
            'patient', 'admission_type', 'treating_doctor', 'department', 'bed',
            'reason_for_admission', 'insurance_info'
        ]
        widgets = {
            'reason_for_admission': forms.Textarea(attrs={'class': 'form-control'}),
            'insurance_info':       forms.TextInput(attrs={'class': 'form-control'}),
            'patient':              forms.Select(attrs={'class': 'form-select'}),
            'admission_type':       forms.Select(attrs={'class': 'form-select'}),
            'treating_doctor':      forms.Select(attrs={'class': 'form-select'}),
            'department':           forms.Select(attrs={'class': 'form-select'}),
            'bed':                  forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        hospital = kwargs.pop('hospital', None)
        super().__init__(*args, **kwargs)
        if hospital:
            self.fields['patient'].queryset        = Patient.objects.filter(hospital=hospital)
            self.fields['treating_doctor'].queryset = Doctor.objects.filter(departments__hospital=hospital)
            self.fields['bed'].queryset            = Bed.objects.filter(
                room__department__hospital=hospital, status='available'
            )
            self.fields['department'].queryset     = Department.objects.filter(hospital=hospital)

class DischargeForm(forms.ModelForm):
    class Meta:
        model   = Admission
        fields  = ['discharge_date', 'discharge_report']
        widgets = {
            'discharge_date': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'discharge_report': forms.Textarea(attrs={'class': 'form-control'}),
        }


    def __init__(self, *args, **kwargs):
        kwargs.pop('hospital', None)
        super().__init__(*args, **kwargs)

class DepartmentForm(forms.ModelForm):
    parent = forms.ModelChoiceField(
        queryset     = Department.objects.all(),
        required     = False,
        empty_label  = "No Parent",
        label        = "Parent Department",
    )

    class Meta:
        model   = Department
        fields  = ['name', 'parent', 'department_type', 'hospital', 'description', 'is_active']
        widgets = {
            'name':             forms.TextInput(attrs={'class': 'form-control'}),
            'parent':           forms.Select(attrs={'class': 'form-select'}),
            'department_type':  forms.Select(attrs={'class': 'form-select'}),
            'hospital':         forms.Select(attrs={'class': 'form-select'}),
            'description':      forms.Textarea(attrs={'class': 'form-control'}),
            'is_active':        forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        hospital = kwargs.pop('hospital', None)
        super().__init__(*args, **kwargs)
        if hospital:
            self.fields['hospital'].queryset = Hospital.objects.filter(id=hospital.id)
            self.fields['hospital'].initial  = hospital
            self.fields['parent'].queryset   = Department.objects.filter(hospital=hospital)

class DoctorForm(forms.ModelForm):
    class Meta:
        model   = Doctor
        fields  = ['user', 'departments']
        widgets = {
            'user':       forms.Select(attrs={'class': 'form-select'}),
            'departments':forms.SelectMultiple(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        hospital = kwargs.pop('hospital', None)
        super().__init__(*args, **kwargs)
        if hospital:
            self.fields['user'].queryset        = CustomUser.objects.filter(hospital=hospital, role='doctor')
            self.fields['departments'].queryset = Department.objects.filter(hospital=hospital)

    def clean(self):
        cleaned = super().clean()
        user  = cleaned.get('user')
        depts = cleaned.get('departments')
        if user and depts and not user.departments.filter(id__in=[d.id for d in depts]).exists():
            raise forms.ValidationError("Selected departments must match the user's assigned departments.")
        return cleaned

class PatientForm(forms.ModelForm):
    # … unchanged – copied exactly from your version …
    birth_year  = forms.IntegerField(min_value=1900, max_value=date.today().year,
                    widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Year'}))
    birth_month = forms.IntegerField(min_value=1, max_value=12,
                    widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Month'}))
    birth_day   = forms.IntegerField(min_value=1, max_value=31,
                    widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Day'}))
    birth_hour  = forms.TimeField(required=False,
                    widget=forms.TimeInput(attrs={'class': 'form-control', 'type': 'time', 'step': '1'}))
    death_hour  = forms.TimeField(required=False,
                    widget=forms.TimeInput(attrs={'class': 'form-control', 'type': 'time', 'step': '1'}))

    class Meta:
        model   = Patient
        fields  = [
            'first_name', 'middle_name', 'last_name',
            'birth_year', 'birth_month', 'birth_day', 'birth_hour', 'death_hour',
            'gender', 'address', 'phone_number', 'whatsapp_number', 'email',
            'occupation', 'religion', 'place_of_birth', 'national_id',
            'photo', 'passport', 'id_card',
            'companion_name', 'companion_phone', 'companion_relationship'
        ]
        widgets = {
            'first_name':        forms.TextInput(attrs={'class': 'form-control'}),
            'middle_name':       forms.TextInput(attrs={'class': 'form-control'}),
            'last_name':         forms.TextInput(attrs={'class': 'form-control'}),
            'gender':            forms.Select(attrs={'class': 'form-select'}),
            'address':           forms.Textarea(attrs={'class': 'form-control'}),
            'phone_number':      forms.TextInput(attrs={'class': 'form-control'}),
            'whatsapp_number':   forms.TextInput(attrs={'class': 'form-control'}),
            'email':             forms.EmailInput(attrs={'class': 'form-control'}),
            'occupation':        forms.TextInput(attrs={'class': 'form-control'}),
            'religion':          forms.TextInput(attrs={'class': 'form-control'}),
            'place_of_birth':    forms.TextInput(attrs={'class': 'form-control'}),
            'national_id':       forms.TextInput(attrs={'class': 'form-control'}),
            'photo':             forms.FileInput(attrs={'class': 'form-control', 'id': 'photo_input'}),
            'passport':          forms.FileInput(attrs={'class': 'form-control', 'id': 'passport_input'}),
            'id_card':           forms.FileInput(attrs={'class': 'form-control', 'id': 'id_card_input'}),
            'companion_name':    forms.TextInput(attrs={'class': 'form-control'}),
            'companion_phone':   forms.TextInput(attrs={'class': 'form-control'}),
            'companion_relationship': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            dob = self.instance.date_of_birth
            if dob:
                self.initial.update({
                    'birth_year':  dob.year,
                    'birth_month': dob.month,
                    'birth_day':   dob.day,
                    'birth_hour':  dob.time() if isinstance(dob, datetime) else None,
                })

    def clean(self):
        cleaned = super().clean()
        if not cleaned.get('passport') and not cleaned.get('id_card'):
            raise forms.ValidationError("At least one ID document (Passport or ID Card) must be provided.")
        y, m, d = cleaned.get('birth_year'), cleaned.get('birth_month'), cleaned.get('birth_day')
        if y and m and d:
            try:
                date(y, m, d)
            except ValueError:
                raise forms.ValidationError("Invalid date of birth.")
        return cleaned

class TransferForm(forms.ModelForm):
    # … identical to the version you posted …
    class Meta:
        model   = Transfer
        fields  = ['transfer_type', 'from_department', 'to_department', 'to_hospital', 'transfer_file', 'new_bed']
        widgets = {
            'transfer_type': forms.Select(attrs={'class': 'form-select'}),
            'from_department': forms.Select(attrs={'class': 'form-select'}),
            'to_department':   forms.Select(attrs={'class': 'form-select'}),
            'to_hospital':     forms.TextInput(attrs={'class': 'form-control'}),
            'transfer_file':   forms.Textarea(attrs={'class': 'form-control'}),
            'new_bed':         forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        hospital = kwargs.pop('hospital', None)
        super().__init__(*args, **kwargs)
        if hospital:
            self.fields['from_department'].queryset = Department.objects.filter(hospital=hospital)
            self.fields['to_department'].queryset   = Department.objects.filter(hospital=hospital)
            self.fields['new_bed'].queryset         = Bed.objects.filter(room__department__hospital=hospital, status='available')
        self.fields['to_department'].required = False
        self.fields['to_hospital'].required   = False
        self.fields['new_bed'].required       = False

    def clean(self):
        cleaned = super().clean()
        ttype = cleaned.get('transfer_type')
        if ttype == 'internal':
            if not cleaned.get('to_department'):
                self.add_error('to_department', 'This field is required for internal transfers.')
            if not cleaned.get('new_bed'):
                self.add_error('new_bed', 'This field is required for internal transfers.')
        elif ttype == 'external' and not cleaned.get('to_hospital'):
            self.add_error('to_hospital', 'This field is required for external transfers.')
        return cleaned

class MedicalRecordForm(forms.ModelForm):
    name = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    dob = forms.DateField(required=False, widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}))
    location = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    mrn = forms.CharField(max_length=50, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    weight = forms.FloatField(required=False, widget=forms.NumberInput(attrs={'class': 'form-control'}))
    height = forms.FloatField(required=False, widget=forms.NumberInput(attrs={'class': 'form-control'}))
    
    SOURCE_HISTORY_CHOICES = [
        ('self', 'Self'), ('family_member', 'Family Member'), ('spouse', 'Spouse'),
        ('significant_other', 'Significant Other'), ('medical_record', 'Medical Record'), ('other', 'Other'),
    ]
    source_history = forms.MultipleChoiceField(choices=SOURCE_HISTORY_CHOICES, required=False, widget=forms.CheckboxSelectMultiple)
    
    PRESENT_BEDSIDE_CHOICES = [
        ('family_member', 'Family Member'), ('significant_other', 'Significant Other'),
        ('medical_personnel', 'Medical Personnel'), ('other', 'Other'),
    ]
    present_at_bedside = forms.MultipleChoiceField(choices=PRESENT_BEDSIDE_CHOICES, required=False, widget=forms.CheckboxSelectMultiple)
    
    REFERRAL_SOURCE_CHOICES = [
        ('self', 'Self'), ('provider', 'Provider'), ('ED', 'ED'), ('health_plan', 'Health Plan'),
        ('direct_physician_admit', 'Direct Physician Admit'), ('recovery_room', 'Recovery Room'), ('other', 'Other'),
    ]
    referral_source = forms.MultipleChoiceField(choices=REFERRAL_SOURCE_CHOICES, required=False, widget=forms.CheckboxSelectMultiple)
    
    HISTORY_LIMITATION_CHOICES = [
        ('none', 'None'), ('clinical_condition', 'Clinical Condition'), ('hearing_impairment', 'Hearing Impairment'),
        ('language_barrier', 'Language Barrier'), ('family_not_available', 'Family or Guardian Not Available'), ('other', 'Other'),
    ]
    history_limitation = forms.MultipleChoiceField(choices=HISTORY_LIMITATION_CHOICES, required=False, widget=forms.CheckboxSelectMultiple)
    
    past_medical_history = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}))
    allergic_history = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}))
    social_history = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}))
    past_surgical_history = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}))
    immunization_history = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}))
    nutritional_history = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}))
    psychiatric_history = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}))
    
    hpi_onset = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 1}))
    hpi_location = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 1}))
    hpi_severity = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 1}))
    hpi_duration = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 1}))
    hpi_modifying_factors = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 1}))
    hpi_others = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 1}))
    
    ROS_CONSTITUTIONAL_CHOICES = [
        ('negative', 'Negative'), ('negative_except_hpi', 'Negative except HPI'), ('fever', 'Fever'),
        ('chills', 'Chills'), ('sweats', 'Sweats'), ('weakness', 'Weakness'), ('fatigue', 'Fatigue'),
        ('decreased_activities', 'Decreased Activities'), ('other', 'Other'),
    ]
    ros_constitutional = forms.MultipleChoiceField(choices=ROS_CONSTITUTIONAL_CHOICES, required=False, widget=forms.CheckboxSelectMultiple)
    
    PHYSICAL_EXAM_GENERAL_CHOICES = [
        ('alert_and_oriented', 'Alert and oriented'), ('no_acute_distress', 'No acute distress'),
        ('mild_distress', 'Mild distress'), ('moderate_distress', 'Moderate distress'),
        ('severe_distress', 'Severe distress'), ('other', 'Other'),
    ]
    physical_exam_general = forms.MultipleChoiceField(choices=PHYSICAL_EXAM_GENERAL_CHOICES, required=False, widget=forms.CheckboxSelectMultiple)
    
    differential_diagnoses = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}))
    result_review = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}))
    interpretation_labs = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}))
    laboratory_results = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}))
    diagnosis = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}))
    course = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}))
    orders = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}))
    professional_service = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}))
    patient_education = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}))
    soap_note = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}))

    class Meta:
        model = MedicalRecord
        fields = [
            'patient', 'complaint', 'medical_history', 'surgical_history', 'medication_history',
            'family_history', 'allergies', 'clinical_examination', 'name', 'dob', 'location',
            'mrn', 'weight', 'height', 'source_history', 'present_at_bedside', 'referral_source',
            'history_limitation', 'past_medical_history', 'allergic_history', 'social_history',
            'past_surgical_history', 'immunization_history', 'nutritional_history', 'psychiatric_history',
            'hpi_onset', 'hpi_location', 'hpi_severity', 'hpi_duration', 'hpi_modifying_factors', 'hpi_others',
            'ros_constitutional', 'physical_exam_general', 'differential_diagnoses', 'result_review',
            'interpretation_labs', 'laboratory_results', 'diagnosis', 'course', 'orders',
            'professional_service', 'patient_education', 'soap_note'
        ]
        widgets = {
            'patient': forms.Select(attrs={'class': 'form-select', 'disabled': 'true'}),
            'complaint': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'medical_history': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'surgical_history': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'medication_history': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'family_history': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'allergies': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'clinical_examination': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        hospital = kwargs.pop('hospital', None)
        patient = kwargs.pop('patient', None)
        super().__init__(*args, **kwargs)
        if hospital:
            self.fields['patient'].queryset = Patient.objects.filter(hospital=hospital)
        if patient:
            self.fields['patient'].initial = patient
            self.fields['patient'].widget.attrs['disabled'] = 'disabled'

    def clean(self):
        cleaned_data = super().clean()
        weight = cleaned_data.get('weight')
        height = cleaned_data.get('height')
        
        if weight and height:
            bmi = weight / ((height / 100) ** 2)
            cleaned_data['bmi'] = round(bmi, 2)
        
        cleaned_data['hpi'] = {
            'onset': cleaned_data.get('hpi_onset'),
            'location': cleaned_data.get('hpi_location'),
            'severity': cleaned_data.get('hpi_severity'),
            'duration': cleaned_data.get('hpi_duration'),
            'modifying_factors': cleaned_data.get('hpi_modifying_factors'),
            'others': cleaned_data.get('hpi_others'),
        }
        
        cleaned_data['ros'] = {'constitutional': cleaned_data.get('ros_constitutional')}
        cleaned_data['physical_exam'] = {'general': cleaned_data.get('physical_exam_general')}
        
        return cleaned_data

class ClinicForm(forms.ModelForm):
    class Meta:
        model   = Clinic
        fields  = ['name', 'clinic_type', 'department', 'doctor', 'hospital']
        widgets = {
            'name':        forms.TextInput(attrs={'class': 'form-control'}),
            'clinic_type': forms.Select(attrs={'class': 'form-select'}),
            'department':  forms.Select(attrs={'class': 'form-select'}),
            'doctor':      forms.Select(attrs={'class': 'form-select'}),
            'hospital':    forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        hospital = kwargs.pop('hospital', None)
        super().__init__(*args, **kwargs)
        if hospital:
            self.fields['department'].queryset = Department.objects.filter(hospital=hospital)
            self.fields['doctor'].queryset     = Doctor.objects.filter(departments__hospital=hospital)
            self.fields['hospital'].queryset   = Hospital.objects.filter(id=hospital.id)
            self.fields['hospital'].initial    = hospital
        self.fields['department'].required = False
        self.fields['doctor'].required     = False

    def clean(self):
        cleaned = super().clean()
        ctype   = cleaned.get('clinic_type')
        dept    = cleaned.get('department')
        doc     = cleaned.get('doctor')

        if ctype == 'department' and not dept:
            self.add_error('department', 'This field is required for department‑based clinics.')
        elif ctype == 'physician' and not doc:
            self.add_error('doctor', 'This field is required for physician‑based clinics.')
        return cleaned
    
class EmergencyDepartmentForm(forms.ModelForm):
    hospital = forms.ModelChoiceField(queryset=Hospital.objects.all(), required=True)
    department = forms.ModelChoiceField(queryset=Department.objects.all(), required=False)
    doctor = forms.ModelChoiceField(queryset=Doctor.objects.all(), required=False)

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['hospital'].queryset = Hospital.objects.filter(id=user.hospital.id)
            self.fields['department'].queryset = Department.objects.filter(hospital=user.hospital)
            self.fields['doctor'].queryset = Doctor.objects.filter(departments__hospital=user.hospital)

    class Meta:
        model = EmergencyDepartment
        fields = ['name', 'hospital', 'emergency_type', 'department', 'doctor', 'location', 'capacity', 'status']
        widgets = {
            'emergency_type': forms.Select(choices=[
                ('trauma', 'Trauma'),
                ('cardiac', 'Cardiac'),
                ('pediatric', 'Pediatric'),
            ]),
            'status': forms.Select(choices=[
                ('active', 'Active'),
                ('inactive', 'Inactive'),
                ('maintenance', 'Under Maintenance'),
            ]),
        }

class SurgicalOperationsDepartmentForm(forms.ModelForm):
    hospital = forms.ModelChoiceField(queryset=Hospital.objects.all(), required=True)
    department = forms.ModelChoiceField(queryset=Department.objects.all(), required=False)
    doctor = forms.ModelChoiceField(queryset=Doctor.objects.all(), required=False)

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['hospital'].queryset = Hospital.objects.filter(id=user.hospital.id)
            self.fields['department'].queryset = Department.objects.filter(hospital=user.hospital)
            self.fields['doctor'].queryset = Doctor.objects.filter(departments__hospital=user.hospital)

    class Meta:
        model = SurgicalOperationsDepartment
        fields = ['name', 'hospital', 'surgical_type', 'department', 'doctor', 'location', 'operating_rooms', 'status']
        widgets = {
            'surgical_type': forms.Select(choices=[
                ('orthopedic', 'Orthopedic'),
                ('neurosurgery', 'Neurosurgery'),
                ('general', 'General'),
            ]),
            'status': forms.Select(choices=[
                ('active', 'Active'),
                ('inactive', 'Inactive'),
                ('maintenance', 'Under Maintenance'),
            ]),
        }

class AppointmentForm(forms.ModelForm):
    class Meta:
        model   = Appointment
        fields  = ['patient', 'clinic', 'department', 'doctor', 'appointment_type', 'date_time', 'notes']
        widgets = {
            'date_time':       forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'notes':           forms.Textarea(attrs={'class': 'form-control'}),
            'patient':         forms.Select(attrs={'class': 'form-select'}),
            'clinic':          forms.Select(attrs={'class': 'form-select'}),
            'department':      forms.Select(attrs={'class': 'form-select'}),
            'doctor':          forms.Select(attrs={'class': 'form-select'}),
            'appointment_type':forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        hospital = kwargs.pop('hospital', None)
        super().__init__(*args, **kwargs)
        if hospital:
            self.fields['patient'].queryset    = Patient.objects.filter(hospital=hospital)
            self.fields['department'].queryset = Department.objects.filter(hospital=hospital)
            self.fields['doctor'].queryset     = Doctor.objects.filter(departments__hospital=hospital)
            self.fields['clinic'].queryset     = Clinic.objects.filter(hospital=hospital)
        if self.initial.get('patient'):
            self.fields['patient'].disabled = True

class VisitForm(forms.ModelForm):
    class Meta:
        model   = Visit
        fields  = ['patient', 'department', 'doctor', 'visit_type', 'notes']
        widgets = {
            'notes':      forms.Textarea(attrs={'class': 'form-control'}),
            'patient':    forms.Select(attrs={'class': 'form-select'}),
            'department': forms.Select(attrs={'class': 'form-select'}),
            'doctor':     forms.Select(attrs={'class': 'form-select'}),
            'visit_type': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        hospital = kwargs.pop('hospital', None)
        super().__init__(*args, **kwargs)
        if hospital:
            self.fields['patient'].queryset    = Patient.objects.filter(hospital=hospital)
            self.fields['department'].queryset = Department.objects.filter(hospital=hospital)
            self.fields['doctor'].queryset     = Doctor.objects.filter(departments__hospital=hospital)

class DiagnosisForm(forms.ModelForm):
    class Meta:
        model  = Diagnosis
        fields = [
            "icd_code", "name", "description", "inclusions", "exclusions",
            "foundation_uri", "index_terms", "coded_elsewhere",
            "related_maternal_codes", "related_perinatal_codes",
            "postcoordination_options", "additional_notes",
            "external_reference_link", "icd_chapter", "internal_notes",
        ]

        widgets = {
            # 👇—— customise the ICD code field for autocomplete ——
            "icd_code": forms.TextInput(attrs={
                "class":       "form-control ctw-input",
                "placeholder": "Enter ICD‑11 code (e.g., BA00)",
                "id":          "id_icd_code",  # Match the ID used in JavaScript
                "autocomplete": "off",
            }),
            "name":               forms.TextInput(attrs={"class": "form-control"}),
            "description":        forms.Textarea(attrs={"class": "form-control", "rows": 4}),
            "inclusions":         forms.Textarea(attrs={"class": "form-control", "rows": 4}),
            "exclusions":         forms.Textarea(attrs={"class": "form-control", "rows": 4}),
            "foundation_uri":     forms.URLInput(attrs={"class": "form-control"}),
            "index_terms":        forms.Textarea(attrs={"class": "form-control", "rows": 4}),
            "coded_elsewhere":    forms.Textarea(attrs={"class": "form-control", "rows": 4}),
            "related_maternal_codes":  forms.Textarea(attrs={"class": "form-control", "rows": 4}),
            "related_perinatal_codes": forms.Textarea(attrs={"class": "form-control", "rows": 4}),
            "postcoordination_options": forms.Textarea(attrs={"class": "form-control", "rows": 4}),
            "additional_notes":   forms.Textarea(attrs={"class": "form-control", "rows": 4}),
            "external_reference_link": forms.URLInput(attrs={"class": "form-control"}),
            "icd_chapter":        forms.TextInput(attrs={"class": "form-control"}),
            "internal_notes":     forms.Textarea(attrs={"class": "form-control", "rows": 4}),
        }

    # --- extra validation / convenience ---------------------------------
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # mark just these two as required; the rest remain optional
        self.fields["icd_code"].required = True
        self.fields["name"].required     = True

    def clean_icd_code(self):
        """
        Normalise the ICD code (uppercase & no surrounding spaces) and
        ensure it roughly matches the ICD‑11 format (letters+digits).
        """
        code = self.cleaned_data["icd_code"].strip().upper()
        if not code:
            raise forms.ValidationError("ICD‑11 code is required.")
        # very loose format check: letter(s) + digit(s), optional dot segment
        import re
        if not re.fullmatch(r"[A-Z]{1,3}[0-9]{1,3}(\.[A-Z0-9]{1,3})?", code):
            raise forms.ValidationError("That doesn't look like a valid ICD‑11 code.")
        return code


class MedicationForm(forms.ModelForm):
    class Meta:
        model   = Medication
        fields  = ['name', 'form', 'quantity', 'price', 'barcode']
        widgets = {
            'name':     forms.TextInput(attrs={'class': 'form-control'}),
            'form':     forms.TextInput(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'price':    forms.NumberInput(attrs={'class': 'form-control'}),
            'barcode':  forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Optional'}),
        }



class MedicationForm(forms.ModelForm):
    class Meta:
        model  = Medication
        fields = ['name', 'form', 'quantity', 'price', 'barcode']
        widgets = {
            'name':     forms.TextInput(attrs={'class': 'form-control'}),
            'form':     forms.TextInput(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'price':    forms.NumberInput(attrs={'class': 'form-control'}),
            'barcode':  forms.TextInput(attrs={'class': 'form-control'}),
        }

class PrescriptionForm(forms.ModelForm):
    send_to_pharmacy = forms.BooleanField(
        required=False,
        label="Send to Pharmacy",
        help_text="If checked, this prescription will automatically be sent to the pharmacy"
    )

    class Meta:
        model  = Prescription
        fields = [
            'patient', 'medication', 'dosage', 'route',
            'number_of_doses', 'total_dose', 'first_dose_date',
            'instructions', 'doctor',
        ]
        widgets = {
            'patient':           forms.HiddenInput(),
            'medication':        forms.Select(attrs={'class': 'form-control'}),
            'dosage':            forms.TextInput(attrs={'class': 'form-control'}),
            'route':             forms.Select(attrs={'class': 'form-control'}),
            'number_of_doses':   forms.NumberInput(attrs={'class': 'form-control'}),
            'total_dose':        forms.NumberInput(attrs={'class': 'form-control'}),
            'first_dose_date':   forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'instructions':      forms.Textarea(attrs={'class': 'form-control'}),
            'doctor':            forms.Select(attrs={'class': 'form-control'}),
        }        

class DispenseActionForm(forms.Form):
    prescription_barcode = forms.CharField(
        label="Prescription Barcode",
        max_length=36,
        widget=forms.TextInput(attrs={"autofocus": True})
    )
    patient_barcode = forms.CharField(
        label="Patient Barcode",
        max_length=36
    )
    action = forms.ChoiceField(
        label="Action",
        choices=DispenseRecord.ACTIONS
    )

class FollowUpForm(forms.ModelForm):
    class Meta:
        model   = FollowUp
        fields  = ['follow_up_date', 'notes']
        widgets = {
            'follow_up_date': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'notes':          forms.Textarea(attrs={'class': 'form-control'}),
        }

class BuildingForm(forms.ModelForm):
    class Meta:
        model   = Building
        fields  = ['name', 'hospital', 'location']
        widgets = {
            'name':     forms.TextInput(attrs={'class': 'form-control'}),
            'hospital': forms.Select(attrs={'class': 'form-select'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        hospital = kwargs.pop('hospital', None)
        super().__init__(*args, **kwargs)
        if hospital:
            self.fields['hospital'].queryset = Hospital.objects.filter(id=hospital.id)
            self.fields['hospital'].initial  = hospital
            self.fields['hospital'].widget.attrs['readonly'] = True

class FloorForm(forms.ModelForm):
    class Meta:
        model   = Floor
        fields  = ['name', 'building', 'floor_number']
        widgets = {
            'name':         forms.TextInput(attrs={'class': 'form-control'}),
            'building':     forms.Select(attrs={'class': 'form-select'}),
            'floor_number': forms.NumberInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        hospital = kwargs.pop('hospital', None)
        super().__init__(*args, **kwargs)
        if hospital:
            self.fields['building'].queryset = Building.objects.filter(hospital=hospital)

class WardForm(forms.ModelForm):
    class Meta:
        model   = Ward
        fields  = ['name', 'floor', 'description']
        widgets = {
            'name':       forms.TextInput(attrs={'class': 'form-control'}),
            'floor':      forms.Select(attrs={'class': 'form-select'}),
            'description':forms.Textarea(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        hospital = kwargs.pop('hospital', None)
        super().__init__(*args, **kwargs)
        if hospital:
            self.fields['floor'].queryset = Floor.objects.filter(building__hospital=hospital)


class RoomForm(forms.ModelForm):
    class Meta:
        model   = Room
        fields  = ['number', 'ward', 'department', 'capacity']
        widgets = {
            'number':     forms.TextInput(attrs={'class': 'form-control'}),
            'ward':       forms.Select(attrs={'class': 'form-select'}),
            'department': forms.Select(attrs={'class': 'form-select'}),
            'capacity':   forms.NumberInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        hospital = kwargs.pop('hospital', None)
        super().__init__(*args, **kwargs)
        if hospital:
            self.fields['ward'].queryset       = Ward.objects.filter(floor__building__hospital=hospital)
            self.fields['department'].queryset = Department.objects.filter(hospital=hospital)


class BedForm(forms.ModelForm):
    building = forms.ModelChoiceField(
        queryset = Building.objects.all(),
        widget   = forms.Select(attrs={'class': 'form-select', 'id': 'id_building'}),
        required = True, label='Building'
    )
    floor = forms.ModelChoiceField(
        queryset = Floor.objects.all(),
        widget   = forms.Select(attrs={'class': 'form-select', 'id': 'id_floor'}),
        required = True, label='Floor'
    )
    ward = forms.ModelChoiceField(
        queryset = Ward.objects.all(),
        widget   = forms.Select(attrs={'class': 'form-select', 'id': 'id_ward'}),
        required = True, label='Ward'
    )
    room = forms.ModelChoiceField(
        queryset = Room.objects.all(),
        widget   = forms.Select(attrs={'class': 'form-select', 'id': 'id_room'}),
        required = True, label='Room'
    )

    class Meta:
        model   = Bed
        fields  = ['bed_number', 'bed_type', 'status', 'room']
        widgets = {
            'bed_number': forms.TextInput(attrs={'class': 'form-control'}),
            'bed_type':   forms.Select(attrs={'class': 'form-select'}),
            'status':     forms.Select(attrs={'class': 'form-select'}),
            'room':       forms.Select(attrs={'class': 'form-select', 'id': 'id_room'}),
        }

    def __init__(self, *args, **kwargs):
        hospital = kwargs.pop('hospital', None)
        super().__init__(*args, **kwargs)
        if hospital:
            self.fields['building'].queryset = Building.objects.filter(hospital=hospital)
            self.fields['floor'].queryset    = Floor.objects.filter(building__hospital=hospital)
            self.fields['ward'].queryset     = Ward.objects.filter(floor__building__hospital=hospital)
            self.fields['room'].queryset     = Room.objects.filter(ward__floor__building__hospital=hospital)
        else:
            for f in ('building', 'floor', 'ward', 'room'):
                self.fields[f].queryset = self.fields[f].queryset.none()

    def clean(self):
        cleaned = super().clean()
        bld, flr, wrd, rm = (cleaned.get(k) for k in ('building', 'floor', 'ward', 'room'))
        if bld and flr and flr.building != bld:
            self.add_error('floor', 'Selected floor does not belong to building.')
        if flr and wrd and wrd.floor != flr:
            self.add_error('ward', 'Selected ward does not belong to floor.')
        if wrd and rm and rm.ward != wrd:
            self.add_error('room', 'Selected room does not belong to ward.')
        return cleaned
    
class RadiologyOrderForm(forms.ModelForm):
    class Meta:
        model   = RadiologyOrder
        fields  = '__all__'
        widgets = {
            'radiology_type': forms.Select(attrs={'class': 'form-control'}),
            'status':         forms.Select(attrs={'class': 'form-control'}),
        }


class BacteriologyResultForm(forms.ModelForm):
    class Meta:
        model   = BacteriologyResult
        fields  = ['patient', 'result', 'notes']
        widgets = {
            'patient': forms.Select(attrs={'class': 'form-select'}),
            'result':  forms.Textarea(attrs={'class': 'form-control'}),
            'notes':   forms.Textarea(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        hospital = kwargs.pop('hospital', None)
        super().__init__(*args, **kwargs)
        if hospital:
            self.fields['patient'].queryset = Patient.objects.filter(hospital=hospital)


class PACSForm(forms.ModelForm):
    class Meta:
        model   = PACS
        fields  = ['patient', 'study_type', 'image_url', 'report', 'study_date']
        widgets = {
            'patient':    forms.Select(attrs={'class': 'form-select'}),
            'study_type': forms.TextInput(attrs={'class': 'form-control'}),
            'image_url':  forms.URLInput(attrs={'class': 'form-control'}),
            'report':     forms.Textarea(attrs={'class': 'form-control'}),
            'study_date': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        hospital = kwargs.pop('hospital', None)
        super().__init__(*args, **kwargs)
        if hospital:
            self.fields['patient'].queryset = Patient.objects.filter(hospital=hospital)

class ProgramForm(forms.ModelForm):
    class Meta:
        model   = Program
        fields  = ['name', 'description']
        widgets = {
            'name':        forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
        }


class FormForm(forms.ModelForm):
    class Meta:
        model   = Form
        fields  = ['patient', 'form_type', 'filled_by', 'date_filled', 'notes']
        widgets = {
            'patient':    forms.Select(attrs={'class': 'form-select'}),
            'form_type':  forms.TextInput(attrs={'class': 'form-control'}),
            'filled_by':  forms.TextInput(attrs={'class': 'form-control'}),
            'date_filled':forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'notes':      forms.Textarea(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        hospital = kwargs.pop('hospital', None)
        super().__init__(*args, **kwargs)
        if hospital:
            self.fields['patient'].queryset = Patient.objects.filter(hospital=hospital)


class ObservationForm(forms.ModelForm):
    class Meta:
        model   = Observation
        fields  = ['patient', 'hospital', 'note', 'timestamp']
        widgets = {
            'timestamp': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def __init__(self, *args, **kwargs):
        hospital = kwargs.pop('hospital', None)
        super().__init__(*args, **kwargs)
        if hospital:
            self.fields['patient'].queryset = Patient.objects.filter(hospital=hospital)

class ProcedureForm(forms.ModelForm):
    class Meta:
        model  = Procedure
        fields = '__all__'          # ← take every real field; no hard‑coded list

    def __init__(self, *args, **kwargs):
        hospital = kwargs.pop('hospital', None)
        super().__init__(*args, **kwargs)

        # Narrow patient / doctor query‑sets **only if those fields exist**
        if hospital:
            if 'patient' in self.fields:
                self.fields['patient'].queryset = Patient.objects.filter(hospital=hospital)
            if 'doctor' in self.fields:
                self.fields['doctor'].queryset  = Doctor.objects.filter(departments__hospital=hospital)

        # Add a generic Bootstrap class to all visible widgets for consistent styling
        for f in self.fields.values():
            if not f.widget.attrs.get('class'):
                f.widget.attrs['class'] = 'form-control'

class PDFSettingsForm(forms.ModelForm):
    """
    Form for customizing PDF layout and settings.
    """
    TABLE_BORDER_COLORS = [
        ('black', 'Black'),
        ('grey', 'Grey'),
        ('darkblue', 'Dark Blue'),
        ('darkgreen', 'Dark Green'),
        ('darkred', 'Dark Red'),
    ]
    
    font_size = forms.IntegerField(
        min_value=8, 
        max_value=14,
        initial=10,
        help_text="Font size for text in tables (8-14)"
    )
    
    table_border_color = forms.ChoiceField(
        choices=TABLE_BORDER_COLORS,
        initial='grey',
        help_text="Color for table borders"
    )
    
    # Content toggle switches
    include_hospital_logo = forms.BooleanField(required=False, initial=True)
    include_patient_details = forms.BooleanField(required=False, initial=True)
    include_medical_records = forms.BooleanField(required=False, initial=True)
    include_companion_info = forms.BooleanField(required=False, initial=True)
    
    # Medical record section toggles
    include_basic_info = forms.BooleanField(required=False, initial=True)
    include_complaint = forms.BooleanField(required=False, initial=True)
    include_allergies = forms.BooleanField(required=False, initial=True)
    include_medical_history = forms.BooleanField(required=False, initial=True)
    include_physical_exam = forms.BooleanField(required=False, initial=True)
    include_diagnosis = forms.BooleanField(required=False, initial=True)
    
    class Meta:
        model = PDFSettings
        fields = [
            'header_text', 'header_image', 'footer_text',
            'font_size', 'table_border_color',
            'include_hospital_logo', 'include_patient_details',
            'include_medical_records', 'include_companion_info',
            'include_basic_info', 'include_complaint',
            'include_allergies', 'include_medical_history',
            'include_physical_exam', 'include_diagnosis',
        ]

    def clean_font_size(self):
        size = self.cleaned_data['font_size']
        if not 8 <= size <= 14:
            raise ValidationError("Font size must be between 8 and 14.")
        return size
    
class ImmunizationForm(forms.ModelForm):
    class Meta:
        model  = Immunization
        fields = ["patient", "vaccine", "date_given", "notes"]
        widgets = {
            "patient":    forms.HiddenInput(),          # pre-filled
            "date_given": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "vaccine":    forms.TextInput(attrs={"class": "form-control"}),
            "notes":      forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }    

class ObsToObsForm(forms.ModelForm):
    class Meta:
        model  = ObsToObs
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
        }        

class VitalSignForm(forms.ModelForm):
    class Meta:
        model = VitalSign
        fields = [
            'taken_at', 'temperature', 'heart_rate', 'respiratory_rate',
            'systolic_bp', 'diastolic_bp', 'oxygen_saturation'
        ]
        widgets = {
            'taken_at': forms.DateTimeInput(
                attrs={'type': 'datetime-local', 'class': 'form-control'}
            ),
            'temperature': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'heart_rate': forms.NumberInput(attrs={'class': 'form-control'}),
            'respiratory_rate': forms.NumberInput(attrs={'class': 'form-control'}),
            'systolic_bp': forms.NumberInput(attrs={'class': 'form-control'}),
            'diastolic_bp': forms.NumberInput(attrs={'class': 'form-control'}),
            'oxygen_saturation': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class FluidBalanceForm(forms.ModelForm):
    class Meta:
        model = FluidBalance
        fields = ['recorded_at', 'intake_ml', 'output_ml']
        widgets = {
            'recorded_at': forms.DateTimeInput(
                attrs={'type': 'datetime-local', 'class': 'form-control'}
            ),
            'intake_ml': forms.NumberInput(attrs={'class': 'form-control'}),
            'output_ml': forms.NumberInput(attrs={'class': 'form-control'}),
        }
        
class PrescriptionRequestForm(forms.ModelForm):
    create_pharmacy_request = forms.ChoiceField(
        choices=[(True, "Yes"), (False, "No")],
        widget=forms.RadioSelect,
        label="Create a pharmacy request?"
    )

    class Meta:
        model = PrescriptionRequest
        fields = ['create_pharmacy_request']

class PrescriptionRequestItemForm(forms.ModelForm):
    medication = forms.ModelChoiceField(
        queryset=Medication.objects.all(),
        widget=forms.Select(attrs={'class':'form-select medication-select'})
    )
    dosage = forms.CharField(
        widget=forms.TextInput(attrs={'class':'form-control dosage-input'})
    )

    class Meta:
        model = PrescriptionRequestItem
        fields = ['medication', 'dosage']

# now the inline formset
PrescriptionRequestItemFormSet = forms.inlineformset_factory(
    PrescriptionRequest,
    PrescriptionRequestItem,
    form=PrescriptionRequestItemForm,
    extra=1,     # start with one row
    can_delete=True,
)        