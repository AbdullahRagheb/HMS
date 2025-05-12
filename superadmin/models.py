from django.db import models


class Hospital(models.Model):
    HOSPITAL_TYPES = [
        ('general', 'General Hospital'),
        ('specialized', 'Specialized Hospital'),
        ('clinic', 'Clinic'),
    ]
    name = models.CharField(max_length=100)
    hospital_type = models.CharField(max_length=20, choices=HOSPITAL_TYPES, default='general')
    location = models.CharField(max_length=200, blank=True)
    address = models.TextField()

    def __str__(self):
        return self.name


class SystemSettings(models.Model):
    system_name = models.CharField(max_length=100, default='Hospital Management System')
    country = models.CharField(max_length=100, default='Unknown')
    logo = models.ImageField(upload_to='logos/', null=True, blank=True)
    main_language = models.CharField(max_length=50, default='English')
    delay_allowance_minutes = models.IntegerField(
        default=15, help_text="Allowed delay time in minutes before deduction applies"
    )
    delay_deduction_percentage = models.DecimalField(
        max_digits=5, decimal_places=2, default=0.5, help_text="Percentage of daily salary to deduct per delay instance"
    )
    absence_deduction_amount = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.00, help_text="Fixed deduction amount per absence."
    )
    # New field for default attendance method
    ATTENDANCE_METHOD_CHOICES = [
        ('fingerprint', 'Fingerprint'),
        ('facial_print', 'Facial Print'),
        ('login_logout', 'Log In and Log Out'),
        ('kpi', 'KPI-Based'),
    ]
    default_attendance_method = models.CharField(
        max_length=20,
        choices=ATTENDANCE_METHOD_CHOICES,
        default='fingerprint',
        help_text="Default attendance method for all employees unless overridden."
    )

    class Meta:
        verbose_name = 'System Settings'
        verbose_name_plural = 'System Settings'

    def __str__(self):
        return self.system_name

    def save(self, *args, **kwargs):
        if SystemSettings.objects.exists() and self.pk is None:
            raise ValueError("Only one SystemSettings instance is allowed.")
        super().save(*args, **kwargs)