from django.contrib.auth.models import AbstractUser
from django.db import models
from datetime import date, datetime, time
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.utils import timezone
from manager.models import Department
from superadmin.models import SystemSettings


class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('super_admin', 'Super Admin'),
        ('doctor', 'Doctor'),
        ('nurse', 'Nurse'),
        ('receptionist', 'Receptionist'),
        ('pharmacist', 'Pharmacist'),
        ('hospital_manager', 'Hospital manager'),
        ('hr', 'Human Resources'),
    ]
    EMPLOYMENT_STATUS_CHOICES = [
        ('active', 'Active'),
        ('suspended', 'Suspended'),
        ('leave', 'Leave'),
    ]
    CONTRACT_TYPE_CHOICES = [
        ('permanent', 'Permanent'),
        ('temporary', 'Temporary'),
        ('contract', 'Contract'),
    ]
    PRACTITIONER_CLASSIFICATION_CHOICES = [
        ('consultant', 'Consultant'),
        ('specialist', 'Specialist'),
        ('second_specialist', 'Second Specialist'),
        ('senior_physician', 'Senior Physician'),
        ('second_physician', 'Second Physician'),
        ('third_physician', 'Third Physician'),
    ]
    ATTENDANCE_METHOD_CHOICES = [
        ('fingerprint', 'Fingerprint'),
        ('facial_print', 'Facial Print'),
        ('login_logout', 'Log In and Log Out'),
        ('kpi', 'KPI-Based'),
    ]

    departments = models.ManyToManyField('manager.Department', blank=True, related_name='users', null=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='hospital_manager')
    hospital = models.ForeignKey(
        'superadmin.Hospital',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        default=None
    )
    hire_date = models.DateField(null=True, blank=True)
    salary_base = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    national_id = models.CharField(max_length=20, unique=True, null=True, blank=True, db_index=True)
    is_active = models.BooleanField(default=True)
    full_name = models.CharField(max_length=200, blank=True)
    job_number = models.CharField(max_length=20, unique=True, blank=True, null=True, db_index=True)
    id_passport_number = models.CharField(max_length=50, blank=True, null=True)
    specialty = models.CharField(max_length=100, blank=True, null=True)
    practitioner_classification = models.CharField(
        max_length=50,
        choices=PRACTITIONER_CLASSIFICATION_CHOICES,
        blank=True,
        null=True,
    )
    contract_type = models.CharField(
        max_length=20,
        choices=CONTRACT_TYPE_CHOICES,
        blank=True,
        null=True,
    )
    benefits = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    allowances = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    employment_status = models.CharField(
        max_length=20,
        choices=EMPLOYMENT_STATUS_CHOICES,
        default='active',
    )
    health_certificate = models.FileField(
        upload_to='health_certificates/',
        blank=True,
        null=True,
    )
    attendance_method = models.CharField(
        max_length=20,
        choices=ATTENDANCE_METHOD_CHOICES,
        blank=True,
        null=True,
        help_text="Individual attendance method; defaults to system setting if blank."
    )

    @property
    def age(self):
        return 0

    def save(self, *args, **kwargs):
        self.full_name = f"{self.first_name} {self.last_name}".strip()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.full_name} ({self.get_role_display()})"

    class Meta:
        indexes = [
            models.Index(fields=['hospital', 'role']),
        ]


class Certificate(models.Model):
    staff = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='certificates')
    certificate_type = models.CharField(max_length=100)
    location_obtained = models.CharField(max_length=200)
    date_obtained = models.DateField()
    copy = models.FileField(upload_to='certificates/', blank=True, null=True)

    def __str__(self):
        return f"{self.certificate_type} - {self.staff.full_name}"


class ProfessionalPracticePermit(models.Model):
    staff = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='practice_permits')
    date_obtained = models.DateField()
    expiry_date = models.DateField()
    copy = models.FileField(upload_to='permits/', blank=True, null=True)

    def __str__(self):
        return f"Permit for {self.staff.full_name} (Expires: {self.expiry_date})"


class HealthInsurance(models.Model):
    staff = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='health_insurances')
    date_obtained = models.DateField()
    issuing_authority = models.CharField(max_length=200)
    expiry_date = models.DateField()
    copy = models.FileField(upload_to='insurance/', blank=True, null=True)

    def __str__(self):
        return f"Insurance for {self.staff.full_name} (Expires: {self.expiry_date})"


class ShiftType(models.Model):
    name = models.CharField(max_length=100)
    start_time = models.TimeField()
    end_time = models.TimeField()

    def __str__(self):
        return self.name

    @property
    def shift_period(self):
        return "morning" if self.start_time.hour < 12 else "night"


class WorkArea(models.Model):
    WORK_AREAS = [
        ('ipd', 'Inpatient Department (IPD)'),
        ('opd', 'Outpatient Clinic (OPD)'),
        ('er', 'Emergency Clinic (ER)'),
        ('ot', 'Operating Theatre (OT)'),
        ('icu', 'Intensive Care Unit'),
        ('ward', 'Ward'),
    ]
    name = models.CharField(max_length=50, choices=WORK_AREAS)
    department = models.ForeignKey('manager.Department', on_delete=models.CASCADE, related_name='work_areas')

    def __str__(self):
        return f"{self.get_name_display()} - {self.department.name}"


class Schedule(models.Model):
    SCHEDULE_TYPE_CHOICES = (
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
    )
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    schedule_type = models.CharField(max_length=20, choices=SCHEDULE_TYPE_CHOICES, default='weekly')
    per_patient_time = models.DurationField(null=True, blank=True)
    shift_period = models.CharField(max_length=20, choices=[('morning', 'Morning'), ('night', 'Night')], blank=True)
    created_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name='created_schedules')
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.department.name} Schedule ({self.start_date} to {self.end_date})"


class StaffDailyAvailability(models.Model):
    DAYS_OF_WEEK = (
        (0, 'Monday'),
        (1, 'Tuesday'),
        (2, 'Wednesday'),
        (3, 'Thursday'),
        (4, 'Friday'),
        (5, 'Saturday'),
        (6, 'Sunday'),
    )
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE, related_name='daily_availability')
    staff = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='daily_availability',
        limit_choices_to={'role__in': ['doctor', 'nurse', 'pharmacist']},
    )
    day_of_week = models.IntegerField(choices=DAYS_OF_WEEK)
    available_from = models.TimeField(null=True, blank=True)
    available_to = models.TimeField(null=True, blank=True)

    class Meta:
        unique_together = ('schedule', 'staff', 'day_of_week')

    def __str__(self):
        return f"{self.staff.full_name} - {self.get_day_of_week_display()}: {self.available_from} to {self.available_to}"


class ShiftAssignment(models.Model):
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE, related_name='shift_assignments')
    staff = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='shift_assignments',
        limit_choices_to={'role__in': ['doctor', 'nurse', 'pharmacist']},
    )
    work_area = models.ForeignKey(WorkArea, on_delete=models.CASCADE)
    shift_type = models.ForeignKey(ShiftType, on_delete=models.CASCADE)
    date = models.DateField()
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Shift for {self.staff.full_name} on {self.date} ({self.shift_type.name})"


class ShiftSwapRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    requester = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='shift_swap_requests',
        limit_choices_to={'role__in': ['doctor', 'nurse', 'pharmacist']},
    )
    requester_shift = models.ForeignKey(
        ShiftAssignment, on_delete=models.CASCADE, related_name='swap_requests_as_requester'
    )
    partner = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='shift_swap_partners',
        limit_choices_to={'role__in': ['doctor', 'nurse', 'pharmacist']},
    )
    partner_shift = models.ForeignKey(
        ShiftAssignment, on_delete=models.CASCADE, related_name='swap_requests_as_partner'
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    request_date = models.DateTimeField(auto_now_add=True)
    approved_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_shift_swaps',
        limit_choices_to={'role': 'hr'},
    )

    def __str__(self):
        return f"Swap: {self.requester.full_name} <-> {self.partner.full_name} on {self.request_date}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.status == 'approved' and self.approved_by:
            self.requester_shift.staff, self.partner_shift.staff = (
                self.partner_shift.staff,
                self.requester_shift.staff,
            )
            self.requester_shift.save()
            self.partner_shift.save()


class Attendance(models.Model):
    staff = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='attendances',
        limit_choices_to={'role__in': ['doctor', 'nurse', 'receptionist', 'pharmacist']},
    )
    shift_assignment = models.ForeignKey(
        ShiftAssignment,
        on_delete=models.CASCADE,
        related_name='attendances',
        null=True,
        blank=True,
    )
    date = models.DateField(default=date.today)
    entry_time = models.DateTimeField(null=True, blank=True)
    exit_time = models.DateTimeField(null=True, blank=True)
    source = models.CharField(
        max_length=20, choices=[('manual', 'Manual'), ('zkteco', 'ZKTeco')], default='manual'
    )
    is_delayed = models.BooleanField(default=False)
    delay_minutes = models.IntegerField(default=0)
    is_absent = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.staff} - {self.date} ({'Absent' if self.is_absent else 'Present'})"

    @property
    def hours_worked(self):
        if self.entry_time and self.exit_time:
            delta = self.exit_time - self.entry_time
            return delta.total_seconds() / 3600
        return 0

    def calculate_delay(self):
        if self.is_absent or not self.entry_time or not self.shift_assignment:
            return
        system_settings = SystemSettings.objects.first()
        if not system_settings:
            return
        
        # Determine attendance method
        attendance_method = self.staff.attendance_method or system_settings.default_attendance_method
        
        if attendance_method == 'kpi' and self.staff.role == 'doctor':
            # TODO: Implement KPI logic once PatientAdmission model is defined
            # Example: Check if doctor has 10 patient admissions
            # admissions = PatientAdmission.objects.filter(
            #     doctor=self.staff,
            #     admission_date=self.date
            # ).count()
            # if admissions < 10:
            #     self.is_absent = True
            #     self.is_delayed = False
            #     self.delay_minutes = 0
            #     self.save()
            #     return
            # else:
            #     self.is_absent = False
            #     self.is_delayed = False
            #     self.delay_minutes = 0
            #     self.save()
            #     return
            self.is_absent = False  # Placeholder: Assume present until KPI logic is implemented
            self.is_delayed = False
            self.delay_minutes = 0
            self.save()
            return
        
        # For fingerprint, facial_print, login_logout
        expected_start = datetime.combine(self.date, self.shift_assignment.shift_type.start_time)
        if self.entry_time > expected_start:
            delay = (self.entry_time - expected_start).total_seconds() / 60
            allowance = system_settings.delay_allowance_minutes
            if delay > allowance + 30:  # 30-minute threshold for absence
                self.is_absent = True
                self.is_delayed = False
                self.delay_minutes = 0
            elif delay > allowance:
                self.is_delayed = True
                self.delay_minutes = int(delay - allowance)
            else:
                self.is_delayed = False
                self.delay_minutes = 0
        else:
            self.is_delayed = False
            self.delay_minutes = 0
        self.save()


class DeductionType(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    is_percentage = models.BooleanField(
        default=False, help_text="If true, amount is a percentage of salary."
    )
    created_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        limit_choices_to={'role': 'hr'},
    )

    def __str__(self):
        return f"{self.name} ({self.amount}{'%' if self.is_percentage else ''})"


class BonusType(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    is_percentage = models.BooleanField(
        default=False, help_text="If true, amount is a percentage of salary."
    )
    created_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        limit_choices_to={'role': 'hr'},
    )

    def __str__(self):
        return f"{self.name} ({self.amount}{'%' if self.is_percentage else ''})"


class Payroll(models.Model):
    staff = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='payrolls',
        limit_choices_to={'role__in': ['doctor', 'nurse', 'receptionist', 'pharmacist']},
    )
    period_start = models.DateField()
    period_end = models.DateField()
    base_salary = models.DecimalField(max_digits=10, decimal_places=2)
    delay_deductions = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    absence_deductions = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    net_salary = models.DecimalField(max_digits=10, decimal_places=2)

    def calculate_deductions(self):
        deductions = sum(deduction.amount for deduction in self.deductions.all())
        return deductions + self.delay_deductions + self.absence_deductions

    def calculate_bonuses(self):
        return sum(bonus.amount for bonus in self.bonuses.all())

    def calculate_delay_deductions(self):
        system_settings = SystemSettings.objects.first()
        if not system_settings:
            return 0
        delay_count = Attendance.objects.filter(
            staff=self.staff,
            date__range=[self.period_start, self.period_end],
            is_delayed=True,
        ).count()
        if delay_count == 0:
            return 0
        days_in_period = (self.period_end - self.period_start).days + 1
        daily_salary = self.base_salary / days_in_period
        deduction_per_delay = daily_salary * (system_settings.delay_deduction_percentage / 100)
        return delay_count * deduction_per_delay

    def calculate_absence_deductions(self):
        system_settings = SystemSettings.objects.first()
        if not system_settings:
            return 0
        absence_count = Attendance.objects.filter(
            staff=self.staff,
            date__range=[self.period_start, self.period_end],
            is_absent=True,
        ).count()
        return absence_count * system_settings.absence_deduction_amount

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.delay_deductions = self.calculate_delay_deductions()
        self.absence_deductions = self.calculate_absence_deductions()
        self.net_salary = self.base_salary + self.calculate_bonuses() - self.calculate_deductions()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.staff} - {self.period_start} to {self.period_end}"


class Deduction(models.Model):
    DEDUCTION_TYPE_CHOICES = [
        ('late_arrival', 'Late Arrival'),
        ('absence', 'Absence'),
        ('policy_violation', 'Policy Violation'),
        ('other', 'Other'),
    ]

    staff = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='deductions',
        limit_choices_to={'role__in': ['doctor', 'nurse', 'receptionist', 'pharmacist']},
    )
    payroll = models.ForeignKey(
        'Payroll',
        on_delete=models.CASCADE,
        related_name='deductions',
        null=True,
        blank=True
    )
    deduction_type = models.CharField(max_length=50, choices=DEDUCTION_TYPE_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField(default=date.today)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.get_deduction_type_display()} for {self.staff.full_name} ({self.amount})"

    def clean(self):
        if self.payroll and self.staff != self.payroll.staff:
            raise ValidationError("Deduction staff must match payroll staff.")
        if self.amount < 0:
            raise ValidationError("Deduction amount cannot be negative.")

    def save(self, *args, **kwargs):
        self.full_clean()  # Run validation
        super().save(*args, **kwargs)


class Bonus(models.Model):
    BONUS_TYPE_CHOICES = [
        ('reward', 'Reward'),
        ('performance', 'Performance'),
        ('holiday', 'Holiday'),
        ('overtime', 'Overtime'),
    ]

    staff = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='bonuses',
        limit_choices_to={'role__in': ['doctor', 'nurse', 'receptionist', 'pharmacist']},
    )
    payroll = models.ForeignKey(
        'Payroll',
        on_delete=models.CASCADE,
        related_name='bonuses',
        null=True,
        blank=True
    )
    bonus_type = models.CharField(max_length=50, choices=BONUS_TYPE_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField(default=date.today)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.get_bonus_type_display()} for {self.staff.full_name} ({self.amount})"

    def clean(self):
        if self.payroll and self.staff != self.payroll.staff:
            raise ValidationError("Bonus staff must match payroll staff.")
        if self.amount < 0:
            raise ValidationError("Bonus amount cannot be negative.")

    def save(self, *args, **kwargs):
        self.full_clean()  # Run validation
        super().save(*args, **kwargs)


class VacationPolicy(models.Model):
    name = models.CharField(max_length=100, unique=True)
    annual_vacation_days = models.IntegerField(default=21)
    reset_date = models.DateField(help_text="Date when vacation days reset annually (e.g., 2025-01-01)")
    created_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        limit_choices_to={'role': 'hr'},
    )

    def __str__(self):
        return f"{self.name} ({self.annual_vacation_days} days)"


class VacationBalance(models.Model):
    staff = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='vacation_balances',
        limit_choices_to={'role__in': ['doctor', 'nurse', 'receptionist', 'pharmacist']},
    )
    policy = models.ForeignKey(VacationPolicy, on_delete=models.CASCADE)
    year = models.IntegerField()
    remaining_days = models.FloatField(default=0.0)
    used_days = models.FloatField(default=0.0)

    class Meta:
        unique_together = ('staff', 'year')

    def __str__(self):
        return f"{self.staff.full_name} - {self.year}: {self.remaining_days} days left"

    def reset_balance(self):
        self.remaining_days = self.policy.annual_vacation_days
        self.used_days = 0
        self.save()


class LeaveRequest(models.Model):
    LEAVE_TYPES = (
        ('vacation', 'Vacation'),
        ('sick', 'Sick Leave'),
        ('personal', 'Personal Leave'),
    )
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    staff = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='leave_requests',
        limit_choices_to={'role__in': ['doctor', 'nurse', 'receptionist', 'pharmacist']},
    )
    leave_type = models.CharField(max_length=20, choices=LEAVE_TYPES, default='vacation')
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    approved_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_leaves',
        limit_choices_to={'role': 'hr'},
    )

    def __str__(self):
        return f"{self.staff} - {self.get_leave_type_display()} ({self.start_date} to {self.end_date})"

    @property
    def days(self):
        return (self.end_date - self.start_date).days + 1

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.status == 'approved' and self.leave_type == 'vacation':
            year = self.start_date.year
            balance, created = VacationBalance.objects.get_or_create(
                staff=self.staff,
                year=year,
                defaults={
                    'policy': VacationPolicy.objects.first(),
                    'remaining_days': VacationPolicy.objects.first().annual_vacation_days,
                },
            )
            balance.used_days += self.days
            balance.remaining_days -= self.days
            balance.save()


class StaffTask(models.Model):
    staff = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='tasks',
        limit_choices_to={'role__in': ['doctor', 'nurse', 'receptionist', 'pharmacist']},
    )
    department = models.ForeignKey('manager.Department', on_delete=models.CASCADE)
    description = models.TextField()
    assigned_date = models.DateField(default=date.today)
    due_date = models.DateField(null=True, blank=True)
    is_completed = models.BooleanField(default=False)

    def __str__(self):
        return f"Task for {self.staff} in {self.department}"