#!/usr/bin/env python
import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

# Import models after Django is set up
from manager.models import Prescription, Patient, Medication
from hr.models import CustomUser
from django.utils import timezone

def create_test_prescription():
    """Create a test prescription programmatically"""
    try:
        # Get first patient
        patient = Patient.objects.first()
        if not patient:
            print("No patient found in the system.")
            return
            
        # Get first doctor user
        doctor = CustomUser.objects.filter(role='doctor').first()
        if not doctor:
            print("No doctor found in the system.")
            return
            
        # Get first medication
        medication = Medication.objects.first()
        if not medication:
            print("No medication found in the system.")
            return
        
        # Create the prescription
        prescription = Prescription.objects.create(
            patient=patient,
            medication=medication,
            dosage=medication.default_dosage or "1 pill daily",
            route="oral",
            number_of_doses=30,
            total_dose=30,
            first_dose_date=timezone.now().date(),
            instructions="Take one pill daily with food",
            doctor=doctor,
            date_prescribed=timezone.now().date()
        )
        
        print(f"Successfully created prescription: {prescription}")
        print(f"Patient: {patient}")
        print(f"Medication: {medication}")
        print(f"Doctor: {doctor}")
        
        # Count all prescriptions
        count = Prescription.objects.count()
        print(f"Total prescriptions in database: {count}")
        
    except Exception as e:
        print(f"Error creating prescription: {str(e)}")

if __name__ == "__main__":
    print("Creating test prescription...")
    create_test_prescription()
    print("Done!") 