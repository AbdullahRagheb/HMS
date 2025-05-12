import datetime
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('hr', '0001_initial'),
        ('manager', '0001_initial'),
        ('superadmin', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='CustomUser',
            name='departments',
            field=models.ManyToManyField(blank=True, related_name='users', to='manager.department'),
        ),
        migrations.AddField(
            model_name='CustomUser',
            name='hospital',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, to='superadmin.hospital'),
        ),
        migrations.CreateModel(
            name='Certificate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('certificate_type', models.CharField(max_length=100)),
                ('location_obtained', models.CharField(max_length=200)),
                ('date_obtained', models.DateField()),
                ('copy', models.FileField(blank=True, null=True, upload_to='certificates/')),
                ('staff', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='certificates', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='HealthInsurance',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_obtained', models.DateField()),
                ('issuing_authority', models.CharField(max_length=200)),
                ('expiry_date', models.DateField()),
                ('copy', models.FileField(blank=True, null=True, upload_to='insurance/')),
                ('staff', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='health_insurances', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ProfessionalPracticePermit',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_obtained', models.DateField()),
                ('expiry_date', models.DateField()),
                ('copy', models.FileField(blank=True, null=True, upload_to='permits/')),
                ('staff', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='practice_permits', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Payroll',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('period_start', models.DateField()),
                ('period_end', models.DateField()),
                ('base_salary', models.DecimalField(decimal_places=2, max_digits=10)),
                ('delay_deductions', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('absence_deductions', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('net_salary', models.DecimalField(decimal_places=2, max_digits=10)),
                ('staff', models.ForeignKey(limit_choices_to={'role__in': ['doctor', 'nurse', 'receptionist', 'pharmacist']}, on_delete=django.db.models.deletion.CASCADE, related_name='payrolls', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Deduction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('applied_date', models.DateField(auto_now_add=True)),
                ('notes', models.TextField(blank=True)),
                ('deduction_type', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='hr.deductiontype')),
                ('payroll', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='deductions', to='hr.payroll')),
            ],
        ),
        migrations.CreateModel(
            name='Bonus',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('applied_date', models.DateField(auto_now_add=True)),
                ('notes', models.TextField(blank=True)),
                ('bonus_type', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='hr.bonustype')),
                ('payroll', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bonuses', to='hr.payroll')),
            ],
        ),
        migrations.CreateModel(
            name='LeaveRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('leave_type', models.CharField(choices=[('vacation', 'Vacation'), ('sick', 'Sick Leave'), ('personal', 'Personal Leave')], default='vacation', max_length=20)),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
                ('reason', models.TextField()),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')], default='pending', max_length=20)),
                ('approved_by', models.ForeignKey(blank=True, limit_choices_to={'role': 'hr'}, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='approved_leaves', to=settings.AUTH_USER_MODEL)),
                ('staff', models.ForeignKey(limit_choices_to={'role__in': ['doctor', 'nurse', 'receptionist', 'pharmacist']}, on_delete=django.db.models.deletion.CASCADE, related_name='leave_requests', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Schedule',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
                ('schedule_type', models.CharField(choices=[('weekly', 'Weekly'), ('monthly', 'Monthly')], default='weekly', max_length=20)),
                ('per_patient_time', models.DurationField(blank=True, help_text='Time allocated per patient', null=True)),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_schedules', to=settings.AUTH_USER_MODEL)),
                ('department', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='schedules', to='manager.department')),
                ('staff', models.ManyToManyField(limit_choices_to={'role__in': ['doctor', 'nurse', 'pharmacist']}, related_name='schedules', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ShiftAssignment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('notes', models.TextField(blank=True, null=True)),
                ('schedule', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='shift_assignments', to='hr.schedule')),
                ('staff', models.ForeignKey(limit_choices_to={'role__in': ['doctor', 'nurse', 'pharmacist']}, on_delete=django.db.models.deletion.CASCADE, related_name='shift_assignments', to=settings.AUTH_USER_MODEL)),
                ('shift_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='hr.shifttype')),
            ],
        ),
        migrations.CreateModel(
            name='Attendance',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(default=datetime.date.today)),
                ('entry_time', models.DateTimeField(blank=True, null=True)),
                ('exit_time', models.DateTimeField(blank=True, null=True)),
                ('source', models.CharField(choices=[('manual', 'Manual'), ('zkteco', 'ZKTeco')], default='manual', max_length=20)),
                ('is_delayed', models.BooleanField(default=False)),
                ('delay_minutes', models.IntegerField(default=0)),
                ('is_absent', models.BooleanField(default=False)),
                ('staff', models.ForeignKey(limit_choices_to={'role__in': ['doctor', 'nurse', 'receptionist', 'pharmacist']}, on_delete=django.db.models.deletion.CASCADE, related_name='attendances', to=settings.AUTH_USER_MODEL)),
                ('shift_assignment', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='attendances', to='hr.shiftassignment')),
            ],
        ),
        migrations.CreateModel(
            name='ShiftSwapRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')], default='pending', max_length=20)),
                ('request_date', models.DateTimeField(auto_now_add=True)),
                ('approved_by', models.ForeignKey(blank=True, limit_choices_to={'role': 'hr'}, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='approved_shift_swaps', to=settings.AUTH_USER_MODEL)),
                ('partner', models.ForeignKey(limit_choices_to={'role__in': ['doctor', 'nurse', 'pharmacist']}, on_delete=django.db.models.deletion.CASCADE, related_name='shift_swap_partners', to=settings.AUTH_USER_MODEL)),
                ('partner_shift', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='swap_requests_as_partner', to='hr.shiftassignment')),
                ('requester', models.ForeignKey(limit_choices_to={'role__in': ['doctor', 'nurse', 'pharmacist']}, on_delete=django.db.models.deletion.CASCADE, related_name='shift_swap_requests', to=settings.AUTH_USER_MODEL)),
                ('requester_shift', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='swap_requests_as_requester', to='hr.shiftassignment')),
            ],
        ),
        migrations.CreateModel(
            name='StaffDailyAvailability',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('day_of_week', models.IntegerField(choices=[(0, 'Monday'), (1, 'Tuesday'), (2, 'Wednesday'), (3, 'Thursday'), (4, 'Friday'), (5, 'Saturday'), (6, 'Sunday')])),
                ('available_from', models.TimeField(blank=True, null=True)),
                ('available_to', models.TimeField(blank=True, null=True)),
                ('schedule', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='daily_availability', to='hr.schedule')),
                ('staff', models.ForeignKey(limit_choices_to={'role__in': ['doctor', 'nurse', 'pharmacist']}, on_delete=django.db.models.deletion.CASCADE, related_name='daily_availability', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='StaffTask',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.TextField()),
                ('assigned_date', models.DateField(default=datetime.date.today)),
                ('due_date', models.DateField(blank=True, null=True)),
                ('is_completed', models.BooleanField(default=False)),
                ('department', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='manager.department')),
                ('staff', models.ForeignKey(limit_choices_to={'role__in': ['doctor', 'nurse', 'receptionist', 'pharmacist']}, on_delete=django.db.models.deletion.CASCADE, related_name='tasks', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='VacationBalance',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('year', models.IntegerField()),
                ('remaining_days', models.FloatField(default=0.0)),
                ('used_days', models.FloatField(default=0.0)),
                ('staff', models.ForeignKey(limit_choices_to={'role__in': ['doctor', 'nurse', 'receptionist', 'pharmacist']}, on_delete=django.db.models.deletion.CASCADE, related_name='vacation_balances', to=settings.AUTH_USER_MODEL)),
                ('policy', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='hr.vacationpolicy')),
            ],
        ),
        migrations.CreateModel(
            name='WorkArea',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(choices=[('ipd', 'Inpatient Department (IPD)'), ('opd', 'Outpatient Clinic (OPD)'), ('er', 'Emergency Clinic (ER)'), ('ot', 'Operating Theatre (OT)'), ('icu', 'Intensive Care Unit'), ('ward', 'Ward')], max_length=50)),
                ('department', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='work_areas', to='manager.department')),
            ],
        ),
        migrations.AddField(
            model_name='BonusType',
            name='created_by',
            field=models.ForeignKey(limit_choices_to={'role': 'hr'}, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='DeductionType',
            name='created_by',
            field=models.ForeignKey(limit_choices_to={'role': 'hr'}, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='VacationPolicy',
            name='created_by',
            field=models.ForeignKey(limit_choices_to={'role': 'hr'}, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='ShiftAssignment',
            name='work_area',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='hr.workarea'),
        ),
        migrations.AddIndex(
            model_name='CustomUser',
            index=models.Index(fields=['hospital', 'role'], name='hr_customus_hospita_095333_idx'),
        ),
        migrations.AlterUniqueTogether(
            name='StaffDailyAvailability',
            unique_together={('schedule', 'staff', 'day_of_week')},
        ),
        migrations.AlterUniqueTogether(
            name='VacationBalance',
            unique_together={('staff', 'year')},
        ),
    ]