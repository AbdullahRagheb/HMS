import datetime
import django.contrib.auth.models
import django.contrib.auth.validators
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True
    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('role', models.CharField(choices=[('super_admin', 'Super Admin'), ('doctor', 'Doctor'), ('nurse', 'Nurse'), ('receptionist', 'Receptionist'), ('pharmacist', 'Pharmacist'), ('hospital_manager', 'Hospital manager'), ('hr', 'Human Resources')], default='hospital_manager', max_length=20)),
                ('hire_date', models.DateField(blank=True, null=True)),
                ('salary_base', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('national_id', models.CharField(blank=True, db_index=True, max_length=20, null=True, unique=True)),
                ('is_active', models.BooleanField(default=True)),
                ('full_name', models.CharField(blank=True, max_length=200)),
                ('job_number', models.CharField(blank=True, db_index=True, max_length=20, null=True, unique=True)),
                ('id_passport_number', models.CharField(blank=True, max_length=50, null=True)),
                ('specialty', models.CharField(blank=True, max_length=100, null=True)),
                ('practitioner_classification', models.CharField(blank=True, choices=[('consultant', 'Consultant'), ('specialist', 'Specialist'), ('second_specialist', 'Second Specialist'), ('senior_physician', 'Senior Physician'), ('second_physician', 'Second Physician'), ('third_physician', 'Third Physician')], max_length=50, null=True)),
                ('contract_type', models.CharField(blank=True, choices=[('permanent', 'Permanent'), ('temporary', 'Temporary'), ('contract', 'Contract')], max_length=20, null=True)),
                ('benefits', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('allowances', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('phone_number', models.CharField(blank=True, max_length=20, null=True)),
                ('email', models.EmailField(blank=True, max_length=254, null=True)),
                ('address', models.TextField(blank=True, null=True)),
                ('employment_status', models.CharField(choices=[('active', 'Active'), ('suspended', 'Suspended'), ('leave', 'Leave')], default='active', max_length=20)),
                ('health_certificate', models.FileField(blank=True, null=True, upload_to='health_certificates/')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='ShiftType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('start_time', models.TimeField()),
                ('end_time', models.TimeField()),
            ],
        ),
        migrations.CreateModel(
            name='BonusType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('description', models.TextField(blank=True)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('is_percentage', models.BooleanField(default=False, help_text='If true, amount is a percentage of salary.')),
            ],
        ),
        migrations.CreateModel(
            name='DeductionType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('description', models.TextField(blank=True)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('is_percentage', models.BooleanField(default=False, help_text='If true, amount is a percentage of salary.')),
            ],
        ),
        migrations.CreateModel(
            name='VacationPolicy',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('annual_vacation_days', models.IntegerField(default=21)),
                ('reset_date', models.DateField(help_text='Date when vacation days reset annually (e.g., 2025-01-01)')),
            ],
        ),
    ]