from django.db import migrations

def create_work_areas(apps, schema_editor):
    Department = apps.get_model('manager', 'Department')
    WorkArea = apps.get_model('hr', 'WorkArea')
    
    # Get all departments
    departments = Department.objects.all()
    
    # Work area choices from the model
    work_areas = [
        'ipd', 'opd', 'er', 'ot', 'icu', 'ward'
    ]
    
    # Create work areas for each department
    for department in departments:
        for area in work_areas:
            WorkArea.objects.get_or_create(
                name=area,
                department=department
            )

def remove_work_areas(apps, schema_editor):
    WorkArea = apps.get_model('hr', 'WorkArea')
    WorkArea.objects.all().delete()

class Migration(migrations.Migration):
    dependencies = [
        ('hr', '0002_add_relationships'),
        ('manager', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_work_areas, remove_work_areas),
    ] 