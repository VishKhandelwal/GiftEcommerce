from django import forms
from .models import DeliveryAddress

class DeliveryAddressForm(forms.ModelForm):
    phone_number = forms.CharField(
        max_length=10,
        min_length=10,
        error_messages={
            'max_length': 'Phone number must be exactly 10 digits.',
            'min_length': 'Phone number must be exactly 10 digits.',
            'required': 'Phone number is required.',
        },
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Phone Number',
            'type': 'tel',
            'pattern': '[1-9][0-9]{9}',  # Prevents leading zero
            'oninput': 'this.value=this.value.replace(/[^0-9]/g, "")',
            'title': 'Enter 10-digit phone number without leading 0'
        })
    )

    pincode = forms.CharField(
        max_length=6,
        min_length=6,
        error_messages={
            'max_length': 'Pincode must be exactly 6 digits.',
            'min_length': 'Pincode must be exactly 6 digits.',
            'required': 'Pincode is required.',
        },
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Pincode',
            'type': 'text',
            'pattern': '[1-9][0-9]{5}',  # Prevents leading zero
            'oninput': 'this.value=this.value.replace(/[^0-9]/g, "")',
            'title': 'Enter 6-digit pincode without leading 0'
        })
    )

    class Meta:
        model = DeliveryAddress
        fields = ['full_name', 'phone_number', 'pincode', 'city', 'state', 'address']
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Full Name'}),
            'city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'City'}),
            'state': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'State'}),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Full Address',
                'rows': 3
            }),
        }
