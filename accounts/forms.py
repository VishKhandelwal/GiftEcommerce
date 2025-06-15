from django import forms

class EmailLoginForm(forms.Form):
    email = forms.EmailField(label="Enter your email")

class OTPVerificationForm(forms.Form):
    otp = forms.CharField(label="Enter OTP")
