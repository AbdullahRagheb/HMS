from django.db import migrations
from django.utils import timezone

def create_shift_types(apps, schema_editor):
    ShiftType = apps.get_model('hr', 'ShiftType')
    
    # Create morning shifts
    ShiftType.objects.get_or_create(
        name='Morning Shift',
        start_time=timezone.datetime.strptime('08:00', '%H:%M').time(),
        end_time=timezone.datetime.strptime('16:00', '%H:%M').time(),
    )
    
    # Create night shifts
    ShiftType.objects.get_or_create(
        name='Night Shift',
        start_time=timezone.datetime.strptime('16:00', '%H:%M').time(),
        end_time=timezone.datetime.strptime('00:00', '%H:%M').time(),
    )

def reverse_shift_types(apps, schema_editor):
    ShiftType = apps.get_model('hr', 'ShiftType')
    ShiftType.objects.all().delete()

class Migration(migrations.Migration):
    dependencies = [
        ('hr', '0006_merge_20250529_1923'),
    ]

    operations = [
        migrations.RunPython(create_shift_types, reverse_shift_types),
    ] 