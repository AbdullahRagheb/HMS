# Generated by Django 5.2 on 2025-05-10 17:47

import django.db.models.deletion
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('manager', '0012_medication_form_medication_price_medication_quantity_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='PharmacyRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('submitted', 'Submitted'), ('accepted', 'Accepted'), ('ready', 'Ready'), ('dispensed', 'Dispensed')], default='submitted', max_length=20)),
                ('token', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('qr_code', models.ImageField(blank=True, upload_to='pharmacy_qrcodes/')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('patient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='manager.patient')),
                ('prescription', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='manager.prescription')),
            ],
        ),
        migrations.CreateModel(
            name='PrescriptionRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_pharmacy_request', models.BooleanField(default=False)),
                ('status', models.CharField(choices=[('submitted', 'Submitted'), ('accepted', 'Accepted'), ('ready', 'Ready'), ('dispensed', 'Dispensed')], default='submitted', max_length=20)),
                ('token', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('qr_code', models.ImageField(blank=True, upload_to='pharmacy_request_qrcodes/')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('patient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='prescription_requests', to='manager.patient')),
            ],
        ),
        migrations.CreateModel(
            name='PrescriptionRequestItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dosage', models.CharField(max_length=100)),
                ('medication', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='manager.medication')),
                ('request', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='manager.prescriptionrequest')),
            ],
        ),
    ]
