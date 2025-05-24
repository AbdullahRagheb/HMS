#!/usr/bin/env python
import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

# Import models after Django is set up
from manager.models import Medication
from django.db import transaction

# List of medications with their details
medications = [
    {
        'name': 'Amoxicillin',
        'form': 'Capsule',
        'quantity': 100,
        'price': 15.99,
        'barcode': 'AMOX12345',
        'default_dosage': '500mg, 3 times daily for 7 days'
    },
    {
        'name': 'Ibuprofen',
        'form': 'Tablet',
        'quantity': 200,
        'price': 8.50,
        'barcode': 'IBUP54321',
        'default_dosage': '400mg, every 6-8 hours as needed for pain'
    },
    {
        'name': 'Paracetamol',
        'form': 'Tablet',
        'quantity': 300,
        'price': 5.99,
        'barcode': 'PARA98765',
        'default_dosage': '500mg, every 4-6 hours as needed (max 4g/day)'
    },
    {
        'name': 'Lisinopril',
        'form': 'Tablet',
        'quantity': 90,
        'price': 12.75,
        'barcode': 'LISI45678',
        'default_dosage': '10mg once daily'
    },
    {
        'name': 'Metformin',
        'form': 'Tablet',
        'quantity': 120,
        'price': 14.99,
        'barcode': 'METF87654',
        'default_dosage': '500mg twice daily with meals'
    },
    {
        'name': 'Atorvastatin',
        'form': 'Tablet',
        'quantity': 30,
        'price': 22.50,
        'barcode': 'ATOR13579',
        'default_dosage': '20mg once daily at bedtime'
    },
    {
        'name': 'Levothyroxine',
        'form': 'Tablet',
        'quantity': 50,
        'price': 18.25,
        'barcode': 'LEVO24680',
        'default_dosage': '50mcg once daily in the morning on empty stomach'
    },
    {
        'name': 'Salbutamol',
        'form': 'Inhaler',
        'quantity': 10,
        'price': 25.99,
        'barcode': 'SALB36925',
        'default_dosage': '2 puffs every 4-6 hours as needed for breathing'
    },
    {
        'name': 'Ceftriaxone',
        'form': 'Injection',
        'quantity': 20,
        'price': 35.00,
        'barcode': 'CEFT14703',
        'default_dosage': '1g IV/IM daily'
    },
    {
        'name': 'Omeprazole',
        'form': 'Capsule',
        'quantity': 60,
        'price': 19.50,
        'barcode': 'OMEP25814',
        'default_dosage': '20mg once daily before breakfast'
    }
]

def add_medications():
    """Add medications to the database if they don't already exist"""
    with transaction.atomic():
        created_count = 0
        existing_count = 0
        
        for med_data in medications:
            # Check if medication with same name and form already exists
            existing = Medication.objects.filter(name=med_data['name'], form=med_data['form']).first()
            
            if existing:
                print(f"Medication already exists: {med_data['name']} ({med_data['form']})")
                existing_count += 1
            else:
                medication = Medication(**med_data)
                medication.save()
                created_count += 1
                print(f"Added medication: {medication.name} ({medication.form})")
        
        print(f"\nSummary: Added {created_count} new medications. {existing_count} already existed.")

if __name__ == '__main__':
    print("Adding medications to the database...")
    add_medications()
    print("Done!") 