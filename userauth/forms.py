from django import forms
from django.contrib.auth.models import User


class RegisterForm(forms.Form):
    email = forms.EmailField(
        label="Email Address",
        widget=forms.EmailInput(attrs={
            "placeholder": "Enter Email Address"
        })
    )

    mobile = forms.CharField(
        label="Mobile Number",
        widget=forms.NumberInput(attrs={
            "placeholder": "Enter Mobile Number"
        })
    )

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()

        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(
                "An account with this email already exists."
            )

        return email


class OTPVerificationForm(forms.Form):
    otp = forms.CharField(
        label="OTP",
        max_length=6,
        min_length=6,
        widget=forms.TextInput(attrs={
            "placeholder": "Enter 6-digit OTP",
            "maxlength": "6",
            "autocomplete": "off"
        })
    )

    def clean_otp(self):
        otp = self.cleaned_data["otp"]

        if not otp.isdigit():
            raise forms.ValidationError("OTP must contain only numbers.")

        return otp


class LoginForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['email']

        widgets = {
            'email': forms.EmailInput(attrs={
                'class': 'form-control w-full px-4 py-3 border-gray-300 border-b-2 focus:outline-none',
                'placeholder': 'Enter email'
            }),
        }
