from .models import Profile, Car, ClientInquiry, Booking
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from django.core.exceptions import ValidationError
from datetime import date

class UserRegistrationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Username',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget = forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password',
        })
        self.fields['password2'].widget = forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm Password',
        })

class LoginForm(forms.Form):
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Username',
            'required': True
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password',
            'required': True
        })
    )

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['role', 'phone_number', 'id_number']
        widgets = {
            'role': forms.Select(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number'}),
            'id_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ID Number (10 digits)'}),
        }

class CarForm(forms.ModelForm):
    class Meta:
        model = Car
        fields = ['model', 'plate', 'price', 'car_type', 'seats', 'engine_type', 'fuel_type', 'size', 'image']
        widgets = {
            'model': forms.TextInput(attrs={'class': 'form-control'}),
            'plate': forms.TextInput(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'car_type': forms.Select(attrs={'class': 'form-control'}),
            'seats': forms.NumberInput(attrs={'class': 'form-control'}),
            'engine_type': forms.TextInput(attrs={'class': 'form-control'}),
            'fuel_type': forms.TextInput(attrs={'class': 'form-control'}),
            'size': forms.TextInput(attrs={'class': 'form-control'}),
        }

class ClientInquiryForm(forms.ModelForm):
    class Meta:
        model = ClientInquiry
        fields = ['client_name', 'client_phone', 'client_email', 'client_id_number', 'message']
        widgets = {
            'client_name': forms.TextInput(attrs={'class': 'form-control'}),
            'client_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'client_email': forms.EmailInput(attrs={'class': 'form-control'}),
            'client_id_number': forms.TextInput(attrs={'class': 'form-control'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def clean_client_id_number(self):
        client_id_number = self.cleaned_data['client_id_number']
        if not client_id_number.isdigit() or len(client_id_number) != 10:
            raise ValidationError('Client ID must be exactly 10 numeric characters.')
        return client_id_number

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['start_date', 'end_date']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        if start_date and end_date:
            if start_date < date.today():
                raise ValidationError('Start date cannot be in the past.')
            if end_date < start_date:
                raise ValidationError('End date must be after start date.')
        return cleaned_data


