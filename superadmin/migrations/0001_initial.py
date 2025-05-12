from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True
    dependencies = []

    operations = [
        migrations.CreateModel(
            name='Hospital',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('hospital_type', models.CharField(choices=[('general', 'General Hospital'), ('specialized', 'Specialized Hospital'), ('clinic', 'Clinic')], default='general', max_length=20)),
                ('location', models.CharField(blank=True, max_length=200)),
                ('address', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='SystemSettings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('system_name', models.CharField(default='Hospital Management System', max_length=100)),
                ('country', models.CharField(default='Unknown', max_length=100)),
                ('logo', models.ImageField(blank=True, null=True, upload_to='logos/')),
                ('main_language', models.CharField(default='English', max_length=50)),
                ('delay_allowance_minutes', models.IntegerField(default=15, help_text='Allowed delay time in minutes before deduction applies')),
                ('delay_deduction_percentage', models.DecimalField(decimal_places=2, default=0.5, help_text='Percentage of daily salary to deduct per delay instance', max_digits=5)),
                ('absence_deduction_amount', models.DecimalField(decimal_places=2, default=0.0, help_text='Fixed deduction amount per absence.', max_digits=10)),
            ],
            options={
                'verbose_name': 'System Settings',
                'verbose_name_plural': 'System Settings',
            },
        ),
    ]