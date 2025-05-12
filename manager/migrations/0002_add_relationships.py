import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('manager', '0001_initial'),
        ('hr', '0001_initial'),
        ('superadmin', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='Doctor',
            name='departments',
            field=models.ManyToManyField(related_name='doctors', to='manager.department'),
        ),
        migrations.AddField(
            model_name='Doctor',
            name='user',
            field=models.OneToOneField(limit_choices_to={'role': 'doctor'}, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='Building',
            name='hospital',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='buildings', to='superadmin.hospital'),
        ),
        migrations.AddField(
            model_name='Patient',
            name='hospital',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='superadmin.hospital'),
        ),
        migrations.CreateModel(
            name='Clinic',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('clinic_type', models.CharField(choices=[('department', 'Department'), ('physician', 'Physician')], max_length=20)),
                ('hospital', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='superadmin.hospital')),
                ('department', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='manager.department')),
                ('doctor', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='manager.doctor')),
            ],
        ),
        migrations.CreateModel(
            name='Floor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('floor_number', models.IntegerField(blank=True, null=True)),
                ('building', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='floors', to='manager.building')),
            ],
        ),
        migrations.CreateModel(
            name='Ward',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField(blank=True)),
                ('floor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='wards', to='manager.floor')),
            ],
        ),
        migrations.CreateModel(
            name='Room',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.CharField(max_length=50)),
                ('capacity', models.IntegerField(default=1)),
                ('department', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='rooms', to='manager.department')),
                ('ward', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='rooms', to='manager.ward')),
            ],
        ),
        migrations.AddField(
            model_name='Bed',
            name='room',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='beds', to='manager.room', verbose_name='الغرفة'),
        ),
        migrations.CreateModel(
            name='MedicalRecord',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('complaint', models.TextField()),
                ('medical_history', models.TextField(blank=True, null=True)),
                ('surgical_history', models.TextField(blank=True, null=True)),
                ('medication_history', models.TextField(blank=True, null=True)),
                ('family_history', models.TextField(blank=True, null=True)),
                ('allergies', models.TextField(blank=True, null=True)),
                ('clinical_examination', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('patient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='manager.patient')),
            ],
        ),
        migrations.CreateModel(
            name='Visit',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('visit_type', models.CharField(choices=[('outpatient', 'Outpatient Clinic'), ('inpatient', 'Inpatient Clinic'), ('surgery', 'Surgery')], max_length=20)),
                ('visit_date', models.DateTimeField(auto_now_add=True)),
                ('notes', models.TextField(blank=True)),
                ('department', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='manager.department')),
                ('doctor', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='manager.doctor')),
                ('patient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='manager.patient')),
            ],
        ),
        migrations.CreateModel(
            name='Prescription',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dosage', models.CharField(max_length=100)),
                ('start_date', models.DateField()),
                ('end_date', models.DateField(blank=True, null=True)),
                ('instructions', models.TextField(blank=True)),
                ('doctor', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='manager.doctor')),
                ('medication', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='manager.medication')),
                ('patient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='manager.patient')),
                ('visit', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='manager.visit')),
            ],
        ),
        migrations.CreateModel(
            name='Diagnosis',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('diagnosis_code', models.CharField(max_length=20)),
                ('description', models.TextField()),
                ('date_diagnosed', models.DateTimeField(auto_now_add=True)),
                ('doctor', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='manager.doctor')),
                ('patient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='manager.patient')),
                ('visit', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='manager.visit')),
            ],
        ),
        migrations.CreateModel(
            name='Appointment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_time', models.DateTimeField()),
                ('status', models.CharField(choices=[('Scheduled', 'Scheduled'), ('Completed', 'Completed'), ('Canceled', 'Canceled'), ('Rescheduled', 'Rescheduled'), ('No Show', 'No Show')], default='Scheduled', max_length=20)),
                ('appointment_type', models.CharField(choices=[('outpatient', 'Outpatient Clinic'), ('inpatient', 'Inpatient Clinic'), ('emergency', 'Emergency Room'), ('surgery', 'Surgery')], default='outpatient', max_length=20)),
                ('notes', models.TextField(blank=True, null=True)),
                ('clinic', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='manager.clinic')),
                ('department', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='manager.department')),
                ('doctor', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='manager.doctor')),
                ('patient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='manager.patient')),
            ],
        ),
        migrations.CreateModel(
            name='Admission',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('admission_date', models.DateTimeField(auto_now_add=True)),
                ('admission_type', models.CharField(choices=[('emergency', 'Emergency'), ('regular', 'Regular'), ('surgical', 'Surgical')], max_length=20)),
                ('reason_for_admission', models.TextField(blank=True, null=True)),
                ('insurance_info', models.CharField(blank=True, max_length=100, null=True)),
                ('discharge_date', models.DateTimeField(blank=True, null=True)),
                ('discharge_report', models.TextField(blank=True, null=True)),
                ('bed', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='manager.bed')),
                ('department', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='manager.department')),
                ('treating_doctor', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='manager.doctor')),
                ('patient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='manager.patient')),
            ],
        ),
        migrations.CreateModel(
            name='FollowUp',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('follow_up_date', models.DateTimeField()),
                ('notes', models.TextField(blank=True)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('completed', 'Completed')], default='pending', max_length=20)),
                ('prescription', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='manager.prescription')),
            ],
        ),
        migrations.CreateModel(
            name='Transfer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('transfer_date', models.DateTimeField(auto_now_add=True)),
                ('transfer_type', models.CharField(choices=[('internal', 'Internal'), ('external', 'External')], max_length=20)),
                ('to_hospital', models.CharField(blank=True, max_length=100, null=True)),
                ('transfer_file', models.TextField(blank=True, null=True)),
                ('admission', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='manager.admission')),
                ('from_department', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='transfers_from', to='manager.department')),
                ('new_bed', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='manager.bed')),
                ('to_department', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='transfers_to', to='manager.department')),
            ],
        ),
    ]