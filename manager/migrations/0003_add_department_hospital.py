import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('manager', '0002_add_relationships'),
        ('superadmin', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='Department',
            name='hospital',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='departments',
                to='superadmin.hospital',
            ),
        ),
    ]