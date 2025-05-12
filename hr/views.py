from datetime import timedelta
from typing import Self
from django.http import JsonResponse
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models import Q
from django.db import transaction
from django.views.decorators.http import require_GET
from .models import (
    CustomUser, StaffTask, Attendance, Schedule, ShiftAssignment, ShiftSwapRequest,
    ShiftType, Payroll, DeductionType, Deduction, BonusType, Bonus,
    VacationPolicy, VacationBalance, LeaveRequest, WorkArea
)
from manager.models import Department, Doctor
from superadmin.models import SystemSettings
from .forms import (
    GlobalBonusForm, GlobalDeductionForm, StaffForm, CertificateFormSet, PracticePermitFormSet, HealthInsuranceFormSet,
    StaffTaskForm, AttendanceForm, ScheduleForm, ShiftAssignmentForm,
    ShiftSwapRequestForm, ShiftSwapApprovalForm, PayrollForm,
    DeductionTypeForm, DeductionFormSet, BonusTypeForm, BonusFormSet,
    VacationPolicyForm, VacationBalanceForm, LeaveRequestForm,
    LeaveApprovalForm, HRSystemSettingsForm, BonusForm, DeductionForm  # Added BonusForm, DeductionForm
)


class HRRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.role == 'hr'


# Staff Views
class StaffListView(LoginRequiredMixin, HRRequiredMixin, ListView):
    model = CustomUser
    template_name = 'staff/staff_list.html'
    context_object_name = 'staff'

    def get_queryset(self):
        return CustomUser.objects.filter(
            hospital=self.request.user.hospital,
            role__in=['doctor', 'nurse', 'receptionist', 'pharmacist']
        )


class StaffCreateView(LoginRequiredMixin, HRRequiredMixin, CreateView):
    model = CustomUser
    form_class = StaffForm
    template_name = 'staff/staff_form.html'
    success_url = reverse_lazy('hr:staff_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['hospital'] = self.request.user.hospital
        return kwargs

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        if self.request.POST:
            data['certificate_formset'] = CertificateFormSet(
                self.request.POST, self.request.FILES, instance=self.object
            )
            data['permit_formset'] = PracticePermitFormSet(
                self.request.POST, self.request.FILES, instance=self.object
            )
            data['insurance_formset'] = HealthInsuranceFormSet(
                self.request.POST, self.request.FILES, instance=self.object
            )
        else:
            data['certificate_formset'] = CertificateFormSet(instance=self.object)
            data['permit_formset'] = PracticePermitFormSet(instance=self.object)
            data['insurance_formset'] = HealthInsuranceFormSet(instance=self.object)
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        certificate_formset = context['certificate_formset']
        permit_formset = context['permit_formset']
        insurance_formset = context['insurance_formset']

        if not (certificate_formset.is_valid() and permit_formset.is_valid() and insurance_formset.is_valid()):
            return self.form_invalid(form)

        staff = form.save(commit=False)
        staff.hospital = self.request.user.hospital
        staff.username = f"{staff.first_name.lower()}{staff.last_name.lower()}{staff.national_id[-4:]}"
        staff.set_password('default_password')
        # Ensure attendance_method is saved (nullable, defaults to system setting if blank)
        staff.attendance_method = form.cleaned_data.get('attendance_method')
        staff.save()

        staff.departments.set(form.cleaned_data['departments'])

        certificate_formset.instance = staff
        certificate_formset.save()
        permit_formset.instance = staff
        permit_formset.save()
        insurance_formset.instance = staff
        insurance_formset.save()

        if staff.role == 'doctor':
            if not staff.departments.exists():
                form.add_error(None, "A doctor must be assigned to at least one department.")
                return self.form_invalid(form)
            doctor = Doctor.objects.create(user=staff)
            doctor.departments.set(staff.departments.all())

        messages.success(self.request, f"Staff {staff} added.")
        return super().form_valid(form)


class StaffUpdateView(LoginRequiredMixin, HRRequiredMixin, UpdateView):
    model = CustomUser
    form_class = StaffForm
    template_name = 'staff/staff_form.html'
    success_url = reverse_lazy('hr:staff_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['hospital'] = self.request.user.hospital
        return kwargs

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        if self.request.POST:
            data['certificate_formset'] = CertificateFormSet(
                self.request.POST, self.request.FILES, instance=self.object
            )
            data['permit_formset'] = PracticePermitFormSet(
                self.request.POST, self.request.FILES, instance=self.object
            )
            data['insurance_formset'] = HealthInsuranceFormSet(
                self.request.POST, self.request.FILES, instance=self.object
            )
        else:
            data['certificate_formset'] = CertificateFormSet(instance=self.object)
            data['permit_formset'] = PracticePermitFormSet(instance=self.object)
            data['insurance_formset'] = HealthInsuranceFormSet(instance=self.object)
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        certificate_formset = context['certificate_formset']
        permit_formset = context['permit_formset']
        insurance_formset = context['insurance_formset']

        if not (certificate_formset.is_valid() and permit_formset.is_valid() and insurance_formset.is_valid()):
            return self.form_invalid(form)

        staff = form.save(commit=False)
        # Ensure attendance_method is updated (nullable, defaults to system setting if blank)
        staff.attendance_method = form.cleaned_data.get('attendance_method')
        staff.save()

        staff.departments.set(form.cleaned_data['departments'])

        certificate_formset.instance = staff
        certificate_formset.save()
        permit_formset.instance = staff
        permit_formset.save()
        insurance_formset.instance = staff
        insurance_formset.save()

        if staff.role == 'doctor':
            if not staff.departments.exists():
                form.add_error(None, "A doctor must be assigned to at least one department.")
                return self.form_invalid(form)
            doctor, created = Doctor.objects.get_or_create(user=staff)
            doctor.departments.set(staff.departments.all())
            doctor.save()

        messages.success(self.request, f"Staff {staff} updated.")
        return super().form_valid(form)

    def get_queryset(self):
        return CustomUser.objects.filter(
            hospital=self.request.user.hospital,
            role__in=['doctor', 'nurse', 'receptionist', 'pharmacist']
        )


class StaffDeleteView(LoginRequiredMixin, HRRequiredMixin, DeleteView):
    model = CustomUser
    template_name = 'staff/staff_confirm_delete.html'
    success_url = reverse_lazy('hr:staff_list')

    def get_queryset(self):
        return CustomUser.objects.filter(
            hospital=self.request.user.hospital,
            role__in=['doctor', 'nurse', 'receptionist', 'pharmacist']
        )


class StaffTaskCreateView(LoginRequiredMixin, HRRequiredMixin, CreateView):
    model = StaffTask
    form_class = StaffTaskForm
    template_name = 'tasks/staff_task_form.html'
    success_url = reverse_lazy('hr:staff_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['hospital'] = self.request.user.hospital
        return kwargs


# Attendance Views
class AttendanceListView(LoginRequiredMixin, HRRequiredMixin, ListView):
    model = Attendance
    template_name = 'attendance/attendance_list.html'
    context_object_name = 'attendances'

    def get_queryset(self):
        return Attendance.objects.filter(staff__hospital=self.request.user.hospital)


class AttendanceCreateView(LoginRequiredMixin, HRRequiredMixin, CreateView):
    model = Attendance
    form_class = AttendanceForm
    template_name = 'attendance/attendance_form.html'
    success_url = reverse_lazy('hr:attendance_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['hospital'] = self.request.user.hospital
        return kwargs

    def form_valid(self, form):
        attendance = form.save(commit=False)
        attendance.save()
        messages.success(self.request, f"Attendance for {attendance.staff} recorded.")
        return super().form_valid(form)


# Schedule Views
class ScheduleListView(LoginRequiredMixin, HRRequiredMixin, ListView):
    model = Schedule
    template_name = 'schedules/schedule_list.html'
    context_object_name = 'schedules'

    def get_queryset(self):
        return Schedule.objects.filter(department__hospital=self.request.user.hospital).order_by('-start_date')


class ScheduleCreateView(LoginRequiredMixin, HRRequiredMixin, CreateView):
    model = Schedule
    form_class = ScheduleForm
    template_name = 'schedules/schedule_form.html'
    success_url = reverse_lazy('hr:schedule_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['hospital'] = self.request.user.hospital
        return kwargs

    def form_valid(self, form):
        with transaction.atomic():
            schedule = form.save(commit=False)
            schedule.created_by = self.request.user
            schedule.save()
            messages.success(self.request, f"Schedule for {schedule.department.name} created successfully.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Failed to create schedule. Please check the form.")
        return super().form_invalid(form)

class ScheduleUpdateView(LoginRequiredMixin, HRRequiredMixin, UpdateView):
    model = Schedule
    form_class = ScheduleForm
    template_name = 'schedules/schedule_form.html'
    success_url = reverse_lazy('hr:schedule_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['hospital'] = self.request.user.hospital
        return kwargs

    def get_queryset(self):
        return Schedule.objects.filter(department__hospital=self.request.user.hospital)

    def form_valid(self, form):
        messages.success(self.request, "Schedule updated successfully.")
        return super().form_valid(form)


class ScheduleDetailView(LoginRequiredMixin, HRRequiredMixin, DetailView):
    model = Schedule
    template_name = 'schedules/schedule_detail.html'
    context_object_name = 'schedule'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['daily_availability'] = self.object.daily_availability.all().order_by('day_of_week')
        context['shift_assignments'] = self.object.shift_assignments.all()
        return context


class ScheduleDeleteView(LoginRequiredMixin, HRRequiredMixin, DeleteView):
    model = Schedule
    template_name = 'schedules/schedule_confirm_delete.html'
    success_url = reverse_lazy('hr:schedule_list')

    def get_queryset(self):
        return Schedule.objects.filter(department__hospital=self.request.user.hospital)


# Shift Assignment Views
class ShiftAssignmentListView(LoginRequiredMixin, ListView):
    model = ShiftAssignment
    template_name = 'shifts/shift_assignment_list.html'
    context_object_name = 'shift_assignments'

    def get_queryset(self):
        queryset = ShiftAssignment.objects.filter(schedule__department__hospital=self.request.user.hospital)
        if self.request.user.role != 'hr':
            queryset = queryset.filter(staff=self.request.user)
        department_id = self.request.GET.get('department')
        date_filter = self.request.GET.get('date')
        if department_id:
            queryset = queryset.filter(schedule__department_id=department_id)
        if date_filter:
            queryset = queryset.filter(date=date_filter)
        return queryset.order_by('date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['schedules'] = Schedule.objects.filter(department__hospital=self.request.user.hospital)
        context['departments'] = Department.objects.filter(hospital=self.request.user.hospital)
        return context

class ShiftAssignmentCreateView(LoginRequiredMixin, HRRequiredMixin, CreateView):
    model = ShiftAssignment
    form_class = ShiftAssignmentForm
    template_name = 'shifts/shift_assignment_form.html'
    success_url = reverse_lazy('hr:shift_assignment_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['hospital'] = self.request.user.hospital
        return kwargs

    def form_valid(self, form):
        with transaction.atomic():
            shift_assignment = form.save(commit=False)
            shift_assignment.save()
            messages.success(self.request, "Shift assignment created successfully.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Failed to create shift assignment. Please check the form.")
        return super().form_invalid(form)

class ShiftAssignmentUpdateView(LoginRequiredMixin, HRRequiredMixin, UpdateView):
    model = ShiftAssignment
    form_class = ShiftAssignmentForm
    template_name = 'shifts/shift_assignment_form.html'
    success_url = reverse_lazy('hr:shift_assignment_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['hospital'] = self.request.user.hospital
        return kwargs

    def get_queryset(self):
        return ShiftAssignment.objects.filter(schedule__department__hospital=self.request.user.hospital)

    def form_valid(self, form):
        with transaction.atomic():
            shift_assignment = form.save(commit=False)
            shift_assignment.save()
            messages.success(self.request, "Shift assignment updated successfully.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Failed to update shift assignment. Please check the form.")
        return super().form_invalid(form)

class ShiftAssignmentDeleteView(LoginRequiredMixin, HRRequiredMixin, DeleteView):
    model = ShiftAssignment
    template_name = 'shifts/shift_assignment_confirm_delete.html'
    success_url = reverse_lazy('hr:shift_assignment_list')

    def get_queryset(self):
        return ShiftAssignment.objects.filter(schedule__department__hospital=self.request.user.hospital)

    def form_valid(self, form):
        messages.success(self.request, "Shift assignment deleted successfully.")
        return super().form_valid(form)

@require_GET
def get_schedule_dates(request):
    schedule_id = request.GET.get('schedule_id')
    if not schedule_id:
        return JsonResponse({'start_date': '', 'end_date': ''})
    
    try:
        schedule = Schedule.objects.get(pk=schedule_id)
        return JsonResponse({
            'start_date': schedule.start_date.isoformat(),
            'end_date': schedule.end_date.isoformat()
        })
    except Schedule.DoesNotExist:
        return JsonResponse({'start_date': '', 'end_date': ''})


class ShiftAssignmentDeleteView(LoginRequiredMixin, HRRequiredMixin, DeleteView):
    model = ShiftAssignment
    template_name = 'shifts/shift_assignment_confirm_delete.html'
    success_url = reverse_lazy('hr:shift_assignment_list')

    def get_queryset(self):
        return ShiftAssignment.objects.filter(schedule__department__hospital=self.request.user.hospital)

    def form_valid(self, form):
        messages.success(self.request, "Shift assignment deleted successfully.")
        return super().form_valid(form)


@require_GET
def get_shift_types(request):
    schedule_id = request.GET.get('schedule_id')
    if not schedule_id:
        return JsonResponse({'shift_types': []})
    
    try:
        schedule = Schedule.objects.get(pk=schedule_id)
        shift_period = schedule.shift_period
        if shift_period:
            shift_types = ShiftType.objects.filter(
                start_time__hour__gte=12 if shift_period == 'night' else 0,
                start_time__hour__lt=12 if shift_period == 'morning' else 24
            ).values('id', 'name')
        else:
            shift_types = ShiftType.objects.all().values('id', 'name')
        return JsonResponse({'shift_types': list(shift_types)})
    except Schedule.DoesNotExist:
        return JsonResponse({'shift_types': []})

# Shift Swap Views
class ShiftSwapRequestCreateView(LoginRequiredMixin, CreateView):
    model = ShiftSwapRequest
    form_class = ShiftSwapRequestForm
    template_name = 'schedules/shift_swap_request_form.html'
    success_url = reverse_lazy('hr:shift_swap_request_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['hospital'] = self.request.user.hospital
        kwargs['requester'] = self.request.user
        kwargs['requester_shift'] = ShiftAssignment.objects.get(id=self.kwargs.get('shift_id'))
        return kwargs

    def form_valid(self, form):
        swap_request = form.save(commit=False)
        swap_request.requester = self.request.user
        swap_request.requester_shift = ShiftAssignment.objects.get(id=self.kwargs.get('shift_id'))
        swap_request.save()
        messages.success(self.request, "Shift swap request submitted.")
        return super().form_valid(form)


class ShiftSwapRequestListView(LoginRequiredMixin, ListView):
    model = ShiftSwapRequest
    template_name = 'shifts/shift_swap_request_list.html'
    context_object_name = 'swap_requests'

    def get_queryset(self):
        if self.request.user.role == 'hr':
            return ShiftSwapRequest.objects.filter(requester__hospital=self.request.user.hospital)
        return ShiftSwapRequest.objects.filter(
            Q(requester=self.request.user) | Q(partner=self.request.user)
        )


class ShiftSwapApprovalView(LoginRequiredMixin, HRRequiredMixin, UpdateView):
    model = ShiftSwapRequest
    form_class = ShiftSwapApprovalForm
    template_name = 'schedules/shift_swap_approval_form.html'
    success_url = reverse_lazy('hr:shift_swap_request_list')

    def form_valid(self, form):
        swap_request = form.save(commit=False)
        swap_request.approved_by = self.request.user
        swap_request.save()
        messages.success(self.request, f"Shift swap request {swap_request.status}.")
        return super().form_valid(form)

    def get_queryset(self):
        return ShiftSwapRequest.objects.filter(requester__hospital=self.request.user.hospital)


# ZKTeco Integration
from zk import ZK, const


def sync_attendance_from_zkteco(request):
    if request.user.role != 'hr':
        return redirect('login')
    zk = ZK('DEVICE_IP', port=4370, timeout=5)
    try:
        conn = zk.connect()
        conn.disable_device()
        attendances = conn.get_attendance()
        for att in attendances:
            staff = CustomUser.objects.filter(national_id=att.user_id, hospital=request.user.hospital).first()
            if staff:
                attendance, created = Attendance.objects.get_or_create(
                    staff=staff,
                    date=att.timestamp.date(),
                    defaults={
                        'entry_time': att.timestamp if att.status == const.MACHINE_STATE_IN else None,
                        'exit_time': att.timestamp if att.status == const.MACHINE_STATE_OUT else None,
                        'source': 'zkteco'
                    }
                )
                if not created:
                    if att.status == const.MACHINE_STATE_IN:
                        attendance.entry_time = att.timestamp
                    elif att.status == const.MACHINE_STATE_OUT:
                        attendance.exit_time = att.timestamp
                    attendance.source = 'zkteco'
                    attendance.save()
        conn.enable_device()
        messages.success(request, "Attendance synced from ZKTeco.")
    except Exception as e:
        messages.error(request, f"Error syncing attendance: {str(e)}")
    finally:
        conn.disconnect()
    return redirect('hr:attendance_list')


# Payroll Views
class PayrollListView(LoginRequiredMixin, HRRequiredMixin, ListView):
    model = Payroll
    template_name = 'payroll/payroll_list.html'
    context_object_name = 'payrolls'

    def get_queryset(self):
        return Payroll.objects.filter(staff__hospital=self.request.user.hospital)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['system_settings'] = SystemSettings.objects.first()
        return context


class PayrollCreateView(LoginRequiredMixin, HRRequiredMixin, CreateView):
    model = Payroll
    form_class = PayrollForm
    template_name = 'payroll/payroll_form.html'
    success_url = reverse_lazy('hr:payroll_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['hospital'] = self.request.user.hospital
        return kwargs

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data['deduction_formset'] = DeductionFormSet()
        data['bonus_formset'] = BonusFormSet()
        return data

    def form_valid(self, form):
        deduction_formset = DeductionFormSet(self.request.POST)
        bonus_formset = BonusFormSet(self.request.POST)

        try:
            with transaction.atomic():
                payroll = form.save(commit=False)
                payroll.save()

                deduction_formset.instance = payroll
                bonus_formset.instance = payroll

                if deduction_formset.is_valid() and bonus_formset.is_valid():
                    deduction_formset.save()
                    bonus_formset.save()
                    messages.success(self.request, f"Payroll for {payroll.staff} created successfully.")
                    return super().form_valid(form)
                else:
                    return self.form_invalid(form)
        except Exception as e:
            messages.error(self.request, f"Error creating payroll: {str(e)}")
            return self.form_invalid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Please correct the errors below.")
        return super().form_invalid(form)


class PayrollUpdateView(LoginRequiredMixin, HRRequiredMixin, UpdateView):
    model = Payroll
    form_class = PayrollForm
    template_name = 'payroll/payroll_form.html'
    success_url = reverse_lazy('hr:payroll_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['hospital'] = self.request.user.hospital
        return kwargs

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        if self.request.POST:
            data['deduction_formset'] = DeductionFormSet(self.request.POST, instance=self.object)
            data['bonus_formset'] = BonusFormSet(self.request.POST, instance=self.object)
        else:
            data['deduction_formset'] = DeductionFormSet(instance=self.object)
            data['bonus_formset'] = BonusFormSet(instance=self.object)
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        deduction_formset = context['deduction_formset']
        bonus_formset = context['bonus_formset']

        try:
            with transaction.atomic():
                payroll = form.save(commit=False)
                payroll.save()

                deduction_formset.instance = payroll
                bonus_formset.instance = payroll

                if deduction_formset.is_valid() and bonus_formset.is_valid():
                    deduction_formset.save()
                    bonus_formset.save()
                    messages.success(self.request, f"Payroll for {payroll.staff} updated successfully.")
                    return super().form_valid(form)
                else:
                    return self.form_invalid(form)
        except Exception as e:
            messages.error(self.request, f"Error updating payroll: {str(e)}")
            return self.form_invalid(form)

    def get_queryset(self):
        return Payroll.objects.filter(staff__hospital=self.request.user.hospital)


class PayrollDeleteView(LoginRequiredMixin, HRRequiredMixin, DeleteView):
    model = Payroll
    template_name = 'payroll/payroll_confirm_delete.html'
    success_url = reverse_lazy('hr:payroll_list')

    def get_queryset(self):
        return Payroll.objects.filter(staff__hospital=self.request.user.hospital)


# Deduction and Bonus Type Views
class DeductionTypeListView(LoginRequiredMixin, HRRequiredMixin, ListView):
    model = DeductionType
    template_name = 'payroll/deduction_type_list.html'
    context_object_name = 'deduction_types'


class DeductionTypeCreateView(LoginRequiredMixin, HRRequiredMixin, CreateView):
    model = DeductionType
    form_class = DeductionTypeForm
    template_name = 'payroll/deduction_type_form.html'
    success_url = reverse_lazy('hr:deduction_type_list')

    def form_valid(self, form):
        messages.success(self.request, "Deduction type created successfully.")
        return super().form_valid(form)


class DeductionTypeUpdateView(LoginRequiredMixin, HRRequiredMixin, UpdateView):
    model = DeductionType
    form_class = DeductionTypeForm
    template_name = 'payroll/deduction_type_form.html'
    success_url = reverse_lazy('hr:deduction_type_list')

    def form_valid(self, form):
        messages.success(self.request, "Deduction type updated successfully.")
        return super().form_valid(form)


class DeductionTypeDeleteView(LoginRequiredMixin, HRRequiredMixin, DeleteView):
    model = DeductionType
    template_name = 'payroll/deduction_type_confirm_delete.html'
    success_url = reverse_lazy('hr:deduction_type_list')


class BonusTypeListView(LoginRequiredMixin, HRRequiredMixin, ListView):
    model = BonusType
    template_name = 'payroll/bonus_type_list.html'
    context_object_name = 'bonus_types'


class BonusTypeCreateView(LoginRequiredMixin, HRRequiredMixin, CreateView):
    model = BonusType
    form_class = BonusTypeForm
    template_name = 'payroll/bonus_type_form.html'
    success_url = reverse_lazy('hr:bonus_type_list')

    def form_valid(self, form):
        messages.success(self.request, "Bonus type created successfully.")
        return super().form_valid(form)


class BonusTypeUpdateView(LoginRequiredMixin, HRRequiredMixin, UpdateView):
    model = BonusType
    form_class = BonusTypeForm
    template_name = 'payroll/bonus_type_form.html'
    success_url = reverse_lazy('hr:bonus_type_list')

    def form_valid(self, form):
        messages.success(self.request, "Bonus type updated successfully.")
        return super().form_valid(form)


class BonusTypeDeleteView(LoginRequiredMixin, HRRequiredMixin, DeleteView):
    model = BonusType
    template_name = 'payroll/bonus_type_confirm_delete.html'
    success_url = reverse_lazy('hr:bonus_type_list')


# Vacation and Leave Views
class VacationPolicyListView(LoginRequiredMixin, HRRequiredMixin, ListView):
    model = VacationPolicy
    template_name = 'leave/vacation_policy_list.html'
    context_object_name = 'vacation_policies'


class VacationPolicyCreateView(LoginRequiredMixin, HRRequiredMixin, CreateView):
    model = VacationPolicy
    form_class = VacationPolicyForm
    template_name = 'leave/vacation_policy_form.html'
    success_url = reverse_lazy('hr:vacation_policy_list')

    def form_valid(self, form):
        messages.success(self.request, "Vacation policy created successfully.")
        return super().form_valid(form)


class VacationPolicyUpdateView(LoginRequiredMixin, HRRequiredMixin, UpdateView):
    model = VacationPolicy
    form_class = VacationPolicyForm
    template_name = 'leave/vacation_policy_form.html'
    success_url = reverse_lazy('hr:vacation_policy_list')

    def form_valid(self, form):
        messages.success(self.request, "Vacation policy updated successfully.")
        return super().form_valid(form)


class VacationPolicyDeleteView(LoginRequiredMixin, HRRequiredMixin, DeleteView):
    model = VacationPolicy
    template_name = 'leave/vacation_policy_confirm_delete.html'
    success_url = reverse_lazy('hr:vacation_policy_list')


class VacationBalanceListView(LoginRequiredMixin, HRRequiredMixin, ListView):
    model = VacationBalance
    template_name = 'leave/vacation_balance_list.html'
    context_object_name = 'vacation_balances'

    def get_queryset(self):
        return VacationBalance.objects.filter(staff__hospital=self.request.user.hospital)


class VacationBalanceCreateView(LoginRequiredMixin, HRRequiredMixin, CreateView):
    model = VacationBalance
    form_class = VacationBalanceForm
    template_name = 'leave/vacation_balance_form.html'
    success_url = reverse_lazy('hr:vacation_balance_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['hospital'] = self.request.user.hospital
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, "Vacation balance created successfully.")
        return super().form_valid(form)


class VacationBalanceUpdateView(LoginRequiredMixin, HRRequiredMixin, UpdateView):
    model = VacationBalance
    form_class = VacationBalanceForm
    template_name = 'leave/vacation_balance_form.html'
    success_url = reverse_lazy('hr:vacation_balance_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['hospital'] = self.request.user.hospital
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, "Vacation balance updated successfully.")
        return super().form_valid(form)

    def get_queryset(self):
        return VacationBalance.objects.filter(staff__hospital=self.request.user.hospital)


class VacationBalanceDeleteView(LoginRequiredMixin, HRRequiredMixin, DeleteView):
    model = VacationBalance
    template_name = 'leave/vacation_balance_confirm_delete.html'
    success_url = reverse_lazy('hr:vacation_balance_list')

    def get_queryset(self):
        return VacationBalance.objects.filter(staff__hospital=self.request.user.hospital)


class LeaveRequestListView(LoginRequiredMixin, HRRequiredMixin, ListView):
    model = LeaveRequest
    template_name = 'leaves/leave_request_list.html'
    context_object_name = 'leave_requests'

    def get_queryset(self):
        return LeaveRequest.objects.filter(staff__hospital=self.request.user.hospital)


class LeaveRequestCreateView(LoginRequiredMixin, CreateView):
    model = LeaveRequest
    form_class = LeaveRequestForm
    template_name = 'leaves/leave_request_form.html'
    success_url = reverse_lazy('hr:leave_request_list')

    def form_valid(self, form):
        leave = form.save(commit=False)
        leave.staff = self.request.user
        leave.save()
        messages.success(self.request, "Leave request submitted.")
        return super().form_valid(form)


class LeaveApprovalView(LoginRequiredMixin, HRRequiredMixin, UpdateView):
    model = LeaveRequest
    form_class = LeaveApprovalForm
    template_name = 'leave/leave_approval_form.html'
    success_url = reverse_lazy('hr:leave_request_list')

    def form_valid(self, form):
        leave = form.save(commit=False)
        leave.approved_by = self.request.user
        leave.save()
        messages.success(self.request, f"Leave request {leave.status}.")
        return super().form_valid(form)

    def get_queryset(self):
        return LeaveRequest.objects.filter(staff__hospital=self.request.user.hospital)


# HR System Settings
class SystemSettingsUpdateView(LoginRequiredMixin, HRRequiredMixin, UpdateView):
    model = SystemSettings
    form_class = HRSystemSettingsForm
    template_name = 'system_settings/system_settings_form.html'
    success_url = reverse_lazy('hr:payroll_list')

    def get_object(self):
        return SystemSettings.objects.first() or SystemSettings.objects.create()

    def form_valid(self, form):
        messages.success(self.request, "HR settings updated successfully.")
        return super().form_valid(form)


# New Bonus and Deduction Views
class GlobalBonusCreateView(LoginRequiredMixin, HRRequiredMixin, CreateView):
    model = Bonus
    form_class = GlobalBonusForm
    template_name = 'payroll/bonus_form.html'
    success_url = reverse_lazy('hr:payroll_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['hospital'] = self.request.user.hospital
        return kwargs

    def form_valid(self, form):
        bonus = form.save(commit=False)
        bonus.save()
        messages.success(self.request, f"Bonus for {bonus.staff.get_full_name()} added successfully.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Please correct the errors below.")
        return super().form_invalid(form)


class GlobalDeductionCreateView(LoginRequiredMixin, HRRequiredMixin, CreateView):
    model = Deduction
    form_class = GlobalDeductionForm
    template_name = 'payroll/deduction_form.html'
    success_url = reverse_lazy('hr:payroll_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['hospital'] = self.request.user.hospital
        return kwargs

    def form_valid(self, form):
        deduction = form.save(commit=False)
        deduction.save()
        messages.success(self.request, f"Deduction for {deduction.staff.get_full_name()} added successfully.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Please correct the errors below.")
        return super().form_invalid(form)
    
    