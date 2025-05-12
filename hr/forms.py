from datetime import date
from django import forms
from django.core.exceptions import ValidationError
from .models import (
    CustomUser, Certificate, ProfessionalPracticePermit, HealthInsurance, ShiftType, StaffDailyAvailability,
    StaffTask, Attendance, Schedule, ShiftAssignment, ShiftSwapRequest,
    Payroll, DeductionType, Deduction, BonusType, Bonus, VacationPolicy,
    VacationBalance, LeaveRequest, SystemSettings, WorkArea
)
from manager.models import Department  # type: ignore


class StaffForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = [
            'first_name', 'last_name', 'national_id', 'job_number', 'id_passport_number',
            'specialty', 'practitioner_classification', 'hire_date', 'contract_type',
            'role', 'departments', 'salary_base', 'benefits', 'allowances',
            'phone_number', 'email', 'address', 'employment_status',
            'health_certificate', 'is_active', 'attendance_method'
        ]
        widgets = {
            'hire_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control'}),
            'health_certificate': forms.FileInput(attrs={'class': 'form-control'}),
            'departments': forms.SelectMultiple(attrs={'class': 'form-select'}),
            'practitioner_classification': forms.Select(attrs={'class': 'form-select'}),
            'contract_type': forms.Select(attrs={'class': 'form-select'}),
            'employment_status': forms.Select(attrs={'class': 'form-select'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'national_id': forms.TextInput(attrs={'class': 'form-control'}),
            'job_number': forms.TextInput(attrs={'class': 'form-control'}),
            'id_passport_number': forms.TextInput(attrs={'class': 'form-control'}),
            'specialty': forms.TextInput(attrs={'class': 'form-control'}),
            'salary_base': forms.NumberInput(attrs={'class': 'form-control'}),
            'benefits': forms.NumberInput(attrs={'class': 'form-control'}),
            'allowances': forms.NumberInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'role': forms.Select(attrs={'class': 'form-select'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'attendance_method': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        hospital = kwargs.pop('hospital', None)
        super().__init__(*args, **kwargs)
        if hospital:
            self.fields['departments'].queryset = Department.objects.filter(hospital=hospital)
        self.fields['role'].choices = [
            ('doctor', 'Doctor'),
            ('nurse', 'Nurse'),
            ('receptionist', 'Receptionist'),
            ('pharmacist', 'Pharmacist'),
        ]
        if self.initial.get('role') == 'doctor' or (self.instance and self.instance.role == 'doctor'):
            self.fields['practitioner_classification'].required = True
        else:
            self.fields['practitioner_classification'].required = False

    def clean(self):
        cleaned_data = super().clean()
        role = cleaned_data.get('role')
        practitioner_classification = cleaned_data.get('practitioner_classification')
        if role == 'doctor' and not practitioner_classification:
            self.add_error('practitioner_classification', 'This field is required for doctors.')
        return cleaned_data


CertificateFormSet = forms.inlineformset_factory(
    CustomUser,
    Certificate,
    fields=('certificate_type', 'location_obtained', 'date_obtained', 'copy'),
    extra=1,
    can_delete=True,
    widgets={
        'certificate_type': forms.TextInput(attrs={'class': 'form-control'}),
        'location_obtained': forms.TextInput(attrs={'class': 'form-control'}),
        'date_obtained': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        'copy': forms.FileInput(attrs={'class': 'form-control'}),
    },
)


PracticePermitFormSet = forms.inlineformset_factory(
    CustomUser,
    ProfessionalPracticePermit,
    fields=('date_obtained', 'expiry_date', 'copy'),
    extra=1,
    can_delete=True,
    widgets={
        'date_obtained': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        'expiry_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        'copy': forms.FileInput(attrs={'class': 'form-control'}),
    },
)


HealthInsuranceFormSet = forms.inlineformset_factory(
    CustomUser,
    HealthInsurance,
    fields=('date_obtained', 'issuing_authority', 'expiry_date', 'copy'),
    extra=1,
    can_delete=True,
    widgets={
        'date_obtained': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        'issuing_authority': forms.TextInput(attrs={'class': 'form-control'}),
        'expiry_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        'copy': forms.FileInput(attrs={'class': 'form-control'}),
    },
)


class StaffTaskForm(forms.ModelForm):
    class Meta:
        model = StaffTask
        fields = ['staff', 'department', 'description', 'due_date', 'is_completed']
        widgets = {
            'due_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'staff': forms.Select(attrs={'class': 'form-select'}),
            'department': forms.Select(attrs={'class': 'form-select'}),
            'is_completed': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        hospital = kwargs.pop('hospital', None)
        super().__init__(*args, **kwargs)
        if hospital:
            self.fields['staff'].queryset = CustomUser.objects.filter(
                hospital=hospital, role__in=['doctor', 'nurse', 'receptionist', 'pharmacist']
            )
            self.fields['department'].queryset = Department.objects.filter(hospital=hospital)


class AttendanceForm(forms.ModelForm):
    class Meta:
        model = Attendance
        fields = ['staff', 'shift_assignment', 'date', 'entry_time', 'exit_time', 'is_absent']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'entry_time': forms.DateTimeInput(
                attrs={'type': 'datetime-local', 'class': 'form-control'}
            ),
            'exit_time': forms.DateTimeInput(
                attrs={'type': 'datetime-local', 'class': 'form-control'}
            ),
            'staff': forms.Select(attrs={'class': 'form-select'}),
            'shift_assignment': forms.Select(attrs={'class': 'form-select'}),
            'is_absent': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        hospital = kwargs.pop('hospital', None)
        super().__init__(*args, **kwargs)
        if hospital:
            self.fields['staff'].queryset = CustomUser.objects.filter(
                hospital=hospital, role__in=['doctor', 'nurse', 'receptionist', 'pharmacist']
            )
            self.fields['shift_assignment'].queryset = ShiftAssignment.objects.filter(
                staff__hospital=hospital
            )

    def clean(self):
        cleaned_data = super().clean()
        is_absent = cleaned_data.get('is_absent')
        entry_time = cleaned_data.get('entry_time')
        exit_time = cleaned_data.get('exit_time')
        if is_absent:
            if entry_time or exit_time:
                raise forms.ValidationError(
                    "If marked as absent, entry and exit times should not be provided."
                )
        else:
            if entry_time and exit_time and exit_time <= entry_time:
                raise forms.ValidationError("Exit time must be after entry time.")
        return cleaned_data


class ScheduleForm(forms.ModelForm):
    per_patient_time = forms.DurationField(
        label="Per Patient Time",
        required=False,
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': 'e.g., 00:30:00'}
        ),
        help_text="Format: HH:MM:SS (e.g., 00:30:00 for 30 minutes)"
    )
    shift_period = forms.ChoiceField(
        choices=[('', 'Select Shift Period'), ('morning', 'Morning'), ('night', 'Night')],
        required=True,
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_shift_period'}),
        label="Shift Period"
    )

    class Meta:
        model = Schedule
        fields = ['department', 'start_date', 'end_date', 'schedule_type', 'per_patient_time', 'shift_period']
        widgets = {
            'department': forms.Select(attrs={'class': 'form-select'}),
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'schedule_type': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        hospital = kwargs.pop('hospital', None)
        super().__init__(*args, **kwargs)
        if hospital:
            self.fields['department'].queryset = Department.objects.filter(hospital=hospital)
        self.fields['start_date'].widget.attrs['min'] = date.today().isoformat()
        self.fields['end_date'].widget.attrs['min'] = date.today().isoformat()

        self.daily_fields = []
        days_of_week = [
            (0, 'Monday'), (1, 'Tuesday'), (2, 'Wednesday'), (3, 'Thursday'),
            (4, 'Friday'), (5, 'Saturday'), (6, 'Sunday')
        ]
        instance = kwargs.get('instance')
        initial_data = {}
        if instance and instance.pk:
            for availability in instance.daily_availability.all():
                initial_data[availability.day_of_week] = {
                    'available_from': availability.available_from,
                    'available_to': availability.available_to,
                }
        for day_value, day_name in days_of_week:
            prefix = f'day_{day_value}'
            initial = initial_data.get(day_value, {})
            available_from_field = forms.TimeField(
                required=False,
                widget=forms.TimeInput(attrs={
                    'type': 'time',
                    'class': 'form-control',
                    'name': f'{prefix}_available_from',
                    'id': f'id_{prefix}_available_from'
                }),
                initial=initial.get('available_from')
            )
            available_to_field = forms.TimeField(
                required=False,
                widget=forms.TimeInput(attrs={
                    'type': 'time',
                    'class': 'form-control',
                    'name': f'{prefix}_available_to',
                    'id': f'id_{prefix}_available_to'
                }),
                initial=initial.get('available_to')
            )
            self.fields[f'{prefix}_available_from'] = available_from_field
            self.fields[f'{prefix}_available_to'] = available_to_field
            self.daily_fields.append({
                'day_name': day_name,
                'day_of_week': day_value,
                'available_from': available_from_field,
                'available_to': available_to_field,
                'available_from_field': f'{prefix}_available_from',
                'available_to_field': f'{prefix}_available_to'
            })

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        schedule_type = cleaned_data.get('schedule_type')
        shift_period = cleaned_data.get('shift_period')

        if start_date and end_date:
            if end_date < start_date:
                self.add_error('end_date', "End date cannot be before start date.")
            if schedule_type == 'weekly' and (end_date - start_date).days > 7:
                self.add_error('end_date', "Weekly schedule cannot exceed 7 days.")
            if schedule_type == 'monthly' and (end_date - start_date).days > 31:
                self.add_error('end_date', "Monthly schedule cannot exceed 31 days.")
        if start_date and start_date < date.today():
            self.add_error('start_date', "Start date cannot be in the past.")

        for day in self.daily_fields:
            prefix = f'day_{day["day_of_week"]}'
            available_from = cleaned_data.get(f'{prefix}_available_from')
            available_to = cleaned_data.get(f'{prefix}_available_to')
            if available_from and available_to:
                if available_to <= available_from:
                    self.add_error(f'{prefix}_available_to', "Available To must be after Available From.")
            elif available_from or available_to:
                self.add_error(
                    f'{prefix}_{"available_from" if available_from else "available_to"}',
                    "Both Available From and Available To must be provided."
                )

        if not shift_period:
            self.add_error('shift_period', "Shift period is required.")

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        if commit:
            instance.save()
            instance.daily_availability.all().delete()
            for day in self.daily_fields:
                prefix = f'day_{day["day_of_week"]}'
                available_from = self.cleaned_data.get(f'{prefix}_available_from')
                available_to = self.cleaned_data.get(f'{prefix}_available_to')
                if available_from and available_to:
                    StaffDailyAvailability.objects.create(
                        schedule=instance,
                        staff=None,
                        day_of_week=day['day_of_week'],
                        available_from=available_from,
                        available_to=available_to
                    )
        return instance

class StaffDailyAvailabilityForm(forms.Form):
    day_of_week = forms.IntegerField(widget=forms.HiddenInput())
    day_name = forms.CharField(widget=forms.HiddenInput(), required=False)
    available_from = forms.TimeField(
        required=False,
        widget=forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
        label="Available From"
    )
    available_to = forms.TimeField(
        required=False,
        widget=forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
        label="Available To"
    )


class ShiftAssignmentForm(forms.ModelForm):
    class Meta:
        model = ShiftAssignment
        fields = ['schedule', 'staff', 'work_area', 'date', 'notes']
        widgets = {
            'schedule': forms.Select(attrs={'class': 'form-select', 'id': 'id_schedule'}),
            # Use ModelMultipleChoiceField with CheckboxSelectMultiple for the staff field
            'staff': forms.SelectMultiple(attrs={'class': 'form-select', 'id': 'id_staff'}),
            'work_area': forms.Select(attrs={'class': 'form-select'}),
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control', 'id': 'id_date'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        hospital = kwargs.pop('hospital', None)
        super().__init__(*args, **kwargs)
        if hospital:
            self.fields['schedule'].queryset = Schedule.objects.filter(department__hospital=hospital)
            self.fields['staff'].queryset = CustomUser.objects.filter(
                hospital=hospital, role__in=['doctor', 'nurse', 'pharmacist']
            )
            self.fields['work_area'].queryset = WorkArea.objects.filter(
                department__hospital=hospital,
                name__in=['طوارئ', 'عمليات', 'OPD', 'ICD']
            )
        self.fields['date'].widget.attrs['min'] = date.today().isoformat()

    def clean(self):
        cleaned_data = super().clean()
        schedule = cleaned_data.get('schedule')
        date = cleaned_data.get('date')
        staff = cleaned_data.get('staff')

        if schedule and date:
            if not (schedule.start_date <= date <= schedule.end_date):
                self.add_error('date', "Shift date must be within the schedule's date range.")
        
        if schedule and staff and date:
            # Check if any of the selected staff are already assigned for this schedule and date
            for person in staff:
                if ShiftAssignment.objects.filter(
                    schedule=schedule, staff=person, date=date
                ).exclude(pk=self.instance.pk).exists():
                    self.add_error(None, f"{person} is already assigned on this date for this schedule.")

        return cleaned_data

class ShiftSwapRequestForm(forms.ModelForm):
    class Meta:
        model = ShiftSwapRequest
        fields = ['partner', 'partner_shift']
        widgets = {
            'partner': forms.Select(attrs={'class': 'form-select'}),
            'partner_shift': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        requester = kwargs.pop('requester', None)
        requester_shift = kwargs.pop('requester_shift', None)
        hospital = kwargs.pop('hospital', None)
        super().__init__(*args, **kwargs)
        if hospital and requester_shift:
            department = requester_shift.schedule.department
            self.fields['partner'].queryset = CustomUser.objects.filter(
                departments=department,
                role__in=['doctor', 'nurse', 'pharmacist']
            ).exclude(id=requester.id)
            self.fields['partner_shift'].queryset = ShiftAssignment.objects.filter(
                schedule__department=department,
                staff__role__in=['doctor', 'nurse', 'pharmacist']
            ).exclude(id=requester_shift.id)

    def clean(self):
        cleaned_data = super().clean()
        partner = cleaned_data.get('partner')
        partner_shift = cleaned_data.get('partner_shift')
        if partner and partner_shift:
            if partner_shift.staff != partner:
                self.add_error('partner_shift', "Selected shift does not belong to the selected partner.")
        return cleaned_data


class ShiftSwapApprovalForm(forms.ModelForm):
    class Meta:
        model = ShiftSwapRequest
        fields = ['status']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'}),
        }


class PayrollForm(forms.ModelForm):
    class Meta:
        model = Payroll
        fields = ['staff', 'period_start', 'period_end', 'base_salary']
        widgets = {
            'period_start': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'period_end': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'base_salary': forms.NumberInput(attrs={'class': 'form-control'}),
            'staff': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        hospital = kwargs.pop('hospital', None)
        super().__init__(*args, **kwargs)
        if hospital:
            self.fields['staff'].queryset = CustomUser.objects.filter(
                hospital=hospital, role__in=['doctor', 'nurse', 'receptionist', 'pharmacist']
            )
        if self.instance and self.instance.id and self.instance.staff:
            self.fields['base_salary'].initial = self.instance.staff.salary_base
        if 'staff' in self.initial:
            try:
                staff = CustomUser.objects.get(id=self.initial['staff'])
                self.fields['base_salary'].initial = staff.salary_base
            except CustomUser.DoesNotExist:
                pass

    def clean(self):
        cleaned_data = super().clean()
        staff = cleaned_data.get('staff')
        period_start = cleaned_data.get('period_start')
        period_end = cleaned_data.get('period_end')
        if not staff:
            raise forms.ValidationError("Please select a staff member.")
        if period_start and period_end and period_end < period_start:
            raise forms.ValidationError("End date cannot be before start date.")
        cleaned_data['base_salary'] = staff.salary_base
        return cleaned_data


class DeductionTypeForm(forms.ModelForm):
    class Meta:
        model = DeductionType
        fields = ['name', 'description', 'amount', 'is_percentage']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'is_percentage': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def clean_amount(self):
        amount = self.cleaned_data['amount']
        is_percentage = self.cleaned_data.get('is_percentage')
        if is_percentage and (amount < 0 or amount > 100):
            raise forms.ValidationError("Percentage must be between 0 and 100.")
        if amount < 0:
            raise forms.ValidationError("Amount cannot be negative.")
        return amount


class BonusTypeForm(forms.ModelForm):
    class Meta:
        model = BonusType
        fields = ['name', 'description', 'amount', 'is_percentage']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'is_percentage': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def clean_amount(self):
        amount = self.cleaned_data['amount']
        is_percentage = self.cleaned_data.get('is_percentage')
        if is_percentage and (amount < 0 or amount > 100):
            raise forms.ValidationError("Percentage must be between 0 and 100.")
        if amount < 0:
            raise forms.ValidationError("Amount cannot be negative.")
        return amount


class DeductionForm(forms.ModelForm):
    class Meta:
        model = Deduction
        fields = ['deduction_type', 'amount', 'notes']
        widgets = {
            'deduction_type': forms.Select(attrs={'class': 'form-select'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control'}),
        }

    def clean_amount(self):
        amount = self.cleaned_data['amount']
        if amount < 0:
            raise forms.ValidationError("Amount cannot be negative.")
        return amount


class BonusForm(forms.ModelForm):
    class Meta:
        model = Bonus
        fields = ['bonus_type', 'amount', 'notes']
        widgets = {
            'bonus_type': forms.Select(attrs={'class': 'form-select'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control'}),
        }

    def clean_amount(self):
        amount = self.cleaned_data['amount']
        if amount < 0:
            raise forms.ValidationError("Amount cannot be negative.")
        return amount


class GlobalDeductionForm(forms.ModelForm):
    DEDUCTION_TYPE_CHOICES = [
        ('late_arrival', 'Late Arrival'),
        ('absence', 'Absence'),
        ('policy_violation', 'Policy Violation'),
        ('other', 'Other'),
    ]

    deduction_type = forms.ChoiceField(
        choices=DEDUCTION_TYPE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = Deduction
        fields = ['staff', 'deduction_type', 'amount', 'notes', 'date', 'payroll']
        widgets = {
            'staff': forms.Select(attrs={'class': 'form-select'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': '3'}),
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'payroll': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        hospital = kwargs.pop('hospital', None)
        super().__init__(*args, **kwargs)
        if hospital:
            self.fields['staff'].queryset = CustomUser.objects.filter(
                hospital=hospital,
                role__in=['doctor', 'nurse', 'receptionist', 'pharmacist']
            )
            self.fields['payroll'].queryset = Payroll.objects.filter(staff__hospital=hospital)
        self.fields['payroll'].required = False

    def clean_amount(self):
        amount = self.cleaned_data['amount']
        if amount < 0:
            raise ValidationError("Amount cannot be negative.")
        return amount

    def clean_date(self):
        date_value = self.cleaned_data['date']
        if date_value < date.today():
            raise ValidationError("Date cannot be in the past.")
        return date_value


class GlobalBonusForm(forms.ModelForm):
    BONUS_TYPE_CHOICES = [
        ('reward', 'Reward'),
        ('performance', 'Performance'),
        ('holiday', 'Holiday'),
        ('overtime', 'Overtime'),
    ]

    bonus_type = forms.ChoiceField(
        choices=BONUS_TYPE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = Bonus
        fields = ['staff', 'bonus_type', 'amount', 'notes', 'date', 'payroll']
        widgets = {
            'staff': forms.Select(attrs={'class': 'form-select'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': '3'}),
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'payroll': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        hospital = kwargs.pop('hospital', None)
        super().__init__(*args, **kwargs)
        if hospital:
            self.fields['staff'].queryset = CustomUser.objects.filter(
                hospital=hospital,
                role__in=['doctor', 'nurse', 'receptionist', 'pharmacist']
            )
            self.fields['payroll'].queryset = Payroll.objects.filter(staff__hospital=hospital)
        self.fields['payroll'].required = False

    def clean_amount(self):
        amount = self.cleaned_data['amount']
        if amount < 0:
            raise ValidationError("Amount cannot be negative.")
        return amount

    def clean_date(self):
        date_value = self.cleaned_data['date']
        if date_value < date.today():
            raise ValidationError("Date cannot be in the past.")
        return date_value


DeductionFormSet = forms.inlineformset_factory(
    Payroll,
    Deduction,
    form=DeductionForm,
    fields=('deduction_type', 'amount', 'notes'),
    extra=1,
    can_delete=True,
    widgets={
        'deduction_type': forms.Select(attrs={'class': 'form-select'}),
        'amount': forms.NumberInput(attrs={'class': 'form-control'}),
        'notes': forms.Textarea(attrs={'class': 'form-control'}),
    },
)


BonusFormSet = forms.inlineformset_factory(
    Payroll,
    Bonus,
    form=BonusForm,
    fields=('bonus_type', 'amount', 'notes'),
    extra=1,
    can_delete=True,
    widgets={
        'bonus_type': forms.Select(attrs={'class': 'form-select'}),
        'amount': forms.NumberInput(attrs={'class': 'form-control'}),
        'notes': forms.Textarea(attrs={'class': 'form-control'}),
    },
)


class VacationPolicyForm(forms.ModelForm):
    class Meta:
        model = VacationPolicy
        fields = ['name', 'annual_vacation_days', 'reset_date']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'annual_vacation_days': forms.NumberInput(attrs={'class': 'form-control'}),
            'reset_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }

    def clean_annual_vacation_days(self):
        days = self.cleaned_data['annual_vacation_days']
        if days < 0:
            raise forms.ValidationError("Annual vacation days cannot be negative.")
        return days


class VacationBalanceForm(forms.ModelForm):
    class Meta:
        model = VacationBalance
        fields = ['staff', 'policy', 'year', 'remaining_days', 'used_days']
        widgets = {
            'staff': forms.Select(attrs={'class': 'form-select'}),
            'policy': forms.Select(attrs={'class': 'form-select'}),
            'year': forms.NumberInput(attrs={'class': 'form-control'}),
            'remaining_days': forms.NumberInput(attrs={'class': 'form-control'}),
            'used_days': forms.NumberInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        hospital = kwargs.pop('hospital', None)
        super().__init__(*args, **kwargs)
        if hospital:
            self.fields['staff'].queryset = CustomUser.objects.filter(
                hospital=hospital, role__in=['doctor', 'nurse', 'receptionist', 'pharmacist']
            )

    def clean(self):
        cleaned_data = super().clean()
        remaining_days = cleaned_data.get('remaining_days')
        used_days = cleaned_data.get('used_days')
        year = cleaned_data.get('year')
        if remaining_days < 0 or used_days < 0:
            raise forms.ValidationError("Days cannot be negative.")
        if year and year < 2000:
            raise forms.ValidationError("Year must be reasonable (after 2000).")
        return cleaned_data


class HRSystemSettingsForm(forms.ModelForm):
    class Meta:
        model = SystemSettings
        fields = ['delay_allowance_minutes', 'delay_deduction_percentage', 'absence_deduction_amount', 'default_attendance_method']
        widgets = {
            'delay_allowance_minutes': forms.NumberInput(
                attrs={'class': 'form-control', 'min': 0}
            ),
            'delay_deduction_percentage': forms.NumberInput(
                attrs={'class': 'form-control', 'min': 0, 'max': 100, 'step': '0.01'}
            ),
            'absence_deduction_amount': forms.NumberInput(
                attrs={'class': 'form-control', 'min': 0}
            ),
            'default_attendance_method': forms.Select(
                attrs={'class': 'form-select'}
            ),
        }
        labels = {
            'delay_allowance_minutes': 'Delay Allowance (Minutes)',
            'delay_deduction_percentage': 'Delay Deduction Percentage (%)',
            'absence_deduction_amount': 'Absence Deduction Amount',
            'default_attendance_method': 'Default Attendance Method',
        }

    def clean_delay_deduction_percentage(self):
        percentage = self.cleaned_data.get('delay_deduction_percentage')
        if percentage < 0 or percentage > 100:
            raise forms.ValidationError("Percentage must be between 0 and 100.")
        return percentage

    def clean_absence_deduction_amount(self):
        amount = self.cleaned_data.get('absence_deduction_amount')
        if amount < 0:
            raise forms.ValidationError("Absence deduction amount cannot be negative.")
        return amount


class LeaveRequestForm(forms.ModelForm):
    class Meta:
        model = LeaveRequest
        fields = ['leave_type', 'start_date', 'end_date', 'reason']
        widgets = {
            'leave_type': forms.Select(attrs={'class': 'form-select'}),
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'reason': forms.Textarea(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        kwargs.pop('hospital', None)
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        if start_date and end_date and end_date < start_date:
            raise forms.ValidationError("End date cannot be before start date.")
        return cleaned_data


class LeaveApprovalForm(forms.ModelForm):
    class Meta:
        model = LeaveRequest
        fields = ['status']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        kwargs.pop('hospital', None)
        super().__init__(*args, **kwargs)
        self.fields['status'].choices = LeaveRequest.STATUS_CHOICES