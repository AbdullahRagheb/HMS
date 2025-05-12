import django.db.models.deletion
import mptt.fields
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True
    dependencies = [
        ('superadmin', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Bed',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bed_number', models.CharField(max_length=10, verbose_name='رقم السرير')),
                ('bed_type', models.CharField(choices=[('regular', 'سرير عادي'), ('icu', 'سرير عناية مركزة'), ('nicu', 'حضانة أطفال'), ('clinic_office', 'مكتب في العيادة الخارجية'), ('er_office', 'مكتب في عيادة الإسعاف')], max_length=20, verbose_name='نوع السرير')),
                ('status', models.CharField(choices=[('available', 'Available'), ('occupied', 'مستخدم'), ('maintenance', 'تحت الصيانة'), ('cleaning', 'قيد التنظيف')], default='available', max_length=20, verbose_name='الحالة')),
            ],
        ),
        migrations.CreateModel(
            name='Medication',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField(blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Building',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('location', models.CharField(blank=True, max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='Department',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('department_type', models.CharField(choices=[('unit', 'Unit'), ('department', 'Department'), ('administration', 'Administration'), ('medical', 'Medical Department'), ('emergency', 'Emergency'), ('surgical', 'Surgical Operations')], default='department', max_length=20)),
                ('description', models.TextField(blank=True, null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('lft', models.PositiveIntegerField(editable=False)),
                ('rght', models.PositiveIntegerField(editable=False)),
                ('tree_id', models.PositiveIntegerField(db_index=True, editable=False)),
                ('level', models.PositiveIntegerField(editable=False)),
                ('parent', mptt.fields.TreeForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children', to='manager.department')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Doctor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='Patient',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=50)),
                ('middle_name', models.CharField(blank=True, max_length=50, null=True)),
                ('last_name', models.CharField(max_length=50)),
                ('birth_year', models.IntegerField(blank=True, null=True)),
                ('birth_month', models.IntegerField(blank=True, null=True)),
                ('birth_day', models.IntegerField(blank=True, null=True)),
                ('birth_hour', models.TimeField(blank=True, null=True)),
                ('death_hour', models.TimeField(blank=True, null=True)),
                ('gender', models.CharField(choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')], max_length=10)),
                ('address', models.TextField()),
                ('phone_number', models.CharField(max_length=20)),
                ('whatsapp_number', models.CharField(blank=True, max_length=20, null=True)),
                ('email', models.EmailField(blank=True, max_length=254, null=True)),
                ('occupation', models.CharField(blank=True, max_length=50, null=True)),
                ('religion', models.CharField(blank=True, max_length=50, null=True)),
                ('place_of_birth', models.CharField(blank=True, max_length=100, null=True)),
                ('mrn', models.CharField(blank=True, max_length=20, unique=True)),
                ('medical_file_number', models.CharField(blank=True, max_length=20, unique=True)),
                ('national_id', models.CharField(max_length=20, unique=True)),
                ('photo', models.ImageField(blank=True, null=True, upload_to='patient_photos/')),
                ('passport', models.ImageField(blank=True, null=True, upload_to='id_documents/')),
                ('id_card', models.ImageField(blank=True, null=True, upload_to='id_documents/')),
                ('companion_name', models.CharField(blank=True, max_length=100, null=True)),
                ('companion_phone', models.CharField(blank=True, max_length=20, null=True)),
                ('companion_relationship', models.CharField(blank=True, choices=[('Parent', 'Parent'), ('Spouse', 'Spouse'), ('Child', 'Child'), ('Sibling', 'Sibling'), ('Friend', 'Friend'), ('Other', 'Other')], max_length=20, null=True)),
            ],
        ),
        migrations.AddConstraint(
            model_name='Patient',
            constraint=models.CheckConstraint(
                condition=models.Q(('passport__isnull', False), ('id_card__isnull', False), _connector='OR'),
                name='at_least_one_id_document'
            ),
        ),
    ]