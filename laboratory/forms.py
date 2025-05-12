from django import forms
from .models import TestOrder

class TestOrderForm(forms.ModelForm):
    class Meta:
        model = TestOrder
        fields = [
            'tests',  
        ]