from django.db import models

# laboratory/models.py
import uuid
from django.db import models
from django.urls import reverse
import qrcode
from io import BytesIO
from django.core.files.base import ContentFile

from manager.models import Patient

class TestGroup(models.Model):
    name = models.CharField(max_length=100)
    tests = models.ManyToManyField('Test')

    def __str__(self):
        return self.name

class Test(models.Model):
    english_name = models.CharField(max_length=200)
    normal_range = models.CharField(max_length=100)
    unit = models.CharField(max_length=50)
    main_category = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.english_name

class TestOrder(models.Model):
    STATUS_SUBMITTED = 'submitted'
    STATUS_ACCEPTED  = 'accepted'
    STATUS_COLLECTED = 'collected'
    STATUS_COMPLETED = 'completed'
    STATUS_CHOICES = [
        (STATUS_SUBMITTED, 'Submitted'),
        (STATUS_ACCEPTED,  'Accepted'),
        (STATUS_COLLECTED, 'Collected'),
        (STATUS_COMPLETED, 'Completed'),
    ]

    patient    = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='lab_orders')
    group      = models.ForeignKey(TestGroup, on_delete=models.SET_NULL, null=True, blank=True)
    tests      = models.ManyToManyField(Test, related_name='orders')
    created_at = models.DateTimeField(auto_now_add=True)
    status     = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_SUBMITTED)
    token      = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    def __str__(self):
        return f"Order #{self.pk} for {self.patient}"

    class Meta:
        ordering = ['-created_at']

class LabRequest(models.Model):
    STATUS_SUBMITTED = 'submitted'
    STATUS_ACCEPTED  = 'accepted'
    STATUS_COLLECTED = 'collected'
    STATUS_COMPLETED = 'completed'
    STATUS_CHOICES = [
        (STATUS_SUBMITTED, 'Submitted'),
        (STATUS_ACCEPTED,  'Accepted'),
        (STATUS_COLLECTED, 'Sample Collected'),
        (STATUS_COMPLETED, 'Completed'),
    ]

    patient     = models.ForeignKey('manager.Patient', on_delete=models.CASCADE)
    group       = models.ForeignKey(TestGroup, on_delete=models.PROTECT, blank=True, null=True)
    tests       = models.ManyToManyField(Test, blank=True)
    status      = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_SUBMITTED)
    token       = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    qr_code     = models.ImageField(upload_to='lab_qrcodes/', blank=True)

    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    def get_scan_url(self):
        return reverse('laboratory:lab_request_scan', args=[str(self.token)])

    def regenerate_qr(self):
        """
        (Re)generate the QR code image for the current token.
        """
        url = self.get_scan_url()
        img = qrcode.make(url)
        buf = BytesIO()
        img.save(buf, format='PNG')
        self.qr_code.save(f"{self.token}.png", ContentFile(buf.getvalue()), save=False)

    def save(self, *args, **kwargs):
        # on every save, regenerate the QR so it always matches the latest token
        super().save(*args, **kwargs)
        self.regenerate_qr()
        super().save(update_fields=['qr_code'])

class Sample(models.Model):
    test_order = models.ForeignKey(
        TestOrder, related_name="samples", on_delete=models.CASCADE
    )
    tube_type = models.CharField(max_length=50, blank=True)
    token     = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    qr_code   = models.ImageField(upload_to="sample_qrcodes/", blank=True)

    def get_scan_url(self):
        # if you ever want to scan the sample QR to do something
        return reverse("laboratory:sample_scan", args=[str(self.token)])

    def save(self, *args, **kwargs):
        # ensure we have a PK/token for the filename
        is_new = self.pk is None
        super().save(*args, **kwargs)

        # Generate QR (pointing at the scan-URL, or just encode the token)
        url = self.get_scan_url()
        img = qrcode.make(url)
        buf = BytesIO()
        img.save(buf, format="PNG")

        # Save into our ImageField
        self.qr_code.save(f"{self.token}.png",
                          ContentFile(buf.getvalue()),
                          save=False)

        super().save(update_fields=["qr_code"])