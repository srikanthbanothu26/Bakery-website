from django import forms
from .models import UserInfo, Address


class UsersForm(forms.ModelForm):
    class Meta:
        model = UserInfo
        fields = ['name', 'email', 'phone', 'address', 'city', 'pincode', 'image']


class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ['phone', 'address', 'city', 'pincode']
        widgets = {
            'address': forms.Textarea(attrs={
                'rows': 2,
                'style': 'resize:none; width: 100%; height: 2.5rem;',
                'class': 'bg-transparent border-0 border-b border-gray-400 focus:outline-none focus:border-[#c6922e] py-2 px-1 text-gray-800'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'bg-transparent border-0 border-b border-gray-400 focus:outline-none focus:border-[#c6922e] py-2 px-1 text-gray-800 w-full'
            }),
            'city': forms.TextInput(attrs={
                'class': 'bg-transparent border-0 border-b border-gray-400 focus:outline-none focus:border-[#c6922e] py-2 px-1 text-gray-800 w-full'
            }),
            'pincode': forms.TextInput(attrs={
                'class': 'bg-transparent border-0 border-b border-gray-400 focus:outline-none focus:border-[#c6922e] py-2 px-1 text-gray-800 w-full'
            }),
        }
