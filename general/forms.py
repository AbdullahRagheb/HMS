from django import forms
from .models import Hospital, SystemSettings


class HospitalForm(forms.ModelForm):
    class Meta:
        model = Hospital
        fields = ['name', 'hospital_type', 'location']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'hospital_type': forms.Select(attrs={'class': 'form-select'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        kwargs.pop('hospital', None)
        super().__init__(*args, **kwargs)


class SuperAdminSystemSettingsForm(forms.ModelForm):
    class Meta:
        model = SystemSettings
        fields = ['system_name', 'country', 'logo', 'main_language']
        widgets = {
            'system_name': forms.TextInput(attrs={'class': 'form-control'}),
            'country': forms.TextInput(attrs={'class': 'form-control'}),
            'logo': forms.FileInput(attrs={'class': 'form-control'}),
            'main_language': forms.TextInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'system_name': 'System Name',
            'country': 'Country',
            'logo': 'Logo',
            'main_language': 'Main Language',
        }