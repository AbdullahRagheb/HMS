from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from hr.models import CustomUser  # Using CustomUser from hr.models
from .models import Hospital, SystemSettings

# Form for CustomUser (used in UserCreateView and UserUpdateView)
class CustomUserCreationForm(UserCreationForm):
    """
    Form for creating a new CustomUser (super admin task).
    Extends UserCreationForm to handle CustomUser fields.
    """
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'first_name', 'last_name', 'role', 'hospital']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'role': forms.Select(attrs={'class': 'form-control'}),
            'hospital': forms.Select(attrs={'class': 'form-control'}),
        }

class CustomUserChangeForm(UserChangeForm):
    """
    Form for updating an existing CustomUser (super admin task).
    Extends UserChangeForm to handle CustomUser fields.
    """
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'first_name', 'last_name', 'role', 'hospital']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'role': forms.Select(attrs={'class': 'form-control'}),
            'hospital': forms.Select(attrs={'class': 'form-control'}),
        }

class HospitalForm(forms.ModelForm):
    manager_username = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label="Manager Username"
    )
    manager_email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control'}),
        label="Manager Email"
    )
    manager_password = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label="Manager Password"
    )

    class Meta:
        model = Hospital
        fields = ['name', 'hospital_type', 'address']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'hospital_type': forms.Select(
                choices=[
                    ('general', 'General Hospital'),
                    ('specialized', 'Specialized Hospital'),
                    ('clinic', 'Clinic'),
                ],
                attrs={'class': 'form-control'}
            ),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def save(self, commit=True):
        hospital = super().save(commit=False)
        if commit:
            hospital.save()
            username = self.cleaned_data['manager_username']
            email = self.cleaned_data['manager_email']
            password = self.cleaned_data['manager_password']
            if CustomUser.objects.filter(username=username).exists():
                raise forms.ValidationError(f"Username '{username}' already exists.")
            CustomUser.objects.create_user(
                username=username,
                email=email,
                password=password,
                role='hospital_manager',
                hospital=hospital
            )
        return hospital

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