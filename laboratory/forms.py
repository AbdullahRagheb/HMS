from django import forms
from .models import TestOrder, Test, TestGroup

class TestOrderForm(forms.ModelForm):
    class Meta:
        model = TestOrder
        fields = [
            'group',
            'tests',
            'notes',  
        ]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.fields.get('group'):
            self.fields['group'].queryset = TestGroup.objects.all().order_by('name')
        if self.fields.get('tests'):
            self.fields['tests'].queryset = Test.objects.all().order_by('english_name')
            self.fields['tests'].help_text = "Select one or more tests to order"


class TestForm(forms.ModelForm):
    class Meta:
        model = Test
        fields = ['english_name', 'normal_range', 'unit', 'main_category']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['english_name'].widget.attrs.update({'autofocus': True})
        self.fields['english_name'].help_text = "Enter the name of the test"
        self.fields['normal_range'].help_text = "Normal reference range for this test"
        self.fields['unit'].help_text = "Measurement unit (e.g., mg/dL, mmol/L)"
        self.fields['main_category'].help_text = "Category for grouping tests (e.g., Hematology, Chemistry)"


class TestGroupForm(forms.ModelForm):
    class Meta:
        model = TestGroup
        fields = ['name', 'tests']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].widget.attrs.update({'autofocus': True})
        self.fields['name'].help_text = "Enter a name for this test group"
        self.fields['tests'].queryset = Test.objects.all().order_by('english_name')
        self.fields['tests'].help_text = "Select the tests to include in this group"