from django.contrib.auth.models import User
from django import forms
from canteen.models import FoodItem
from .models import *
class LoginRegisterForm(forms.Form):
    username = forms.CharField(label='Roll Number', max_length=20)
    password = forms.CharField(label='Password', widget=forms.PasswordInput)

    def clean_username(self):
        username = self.cleaned_data['username']
        if RFID.objects.filter(roll_number=username).exists():
            return username
        else:
            raise forms.ValidationError('Invalid roll number. Please enter a valid roll number.')

class FoodItemForm(forms.ModelForm):
    class Meta:
        model = FoodItem
        fields = ['name', 'price', 'description', 'image',]  # Include 'image' field to allow image uploads
    
    def __init__(self, *args, **kwargs):
        super(FoodItemForm, self).__init__(*args, **kwargs)
        self.fields['name'].widget.attrs.update({'class': 'form-control'})
        self.fields['price'].widget.attrs.update({'class': 'form-control'})
        self.fields['description'].widget.attrs.update({'class': 'form-control'})
        self.fields['image'].widget.attrs.update({'class': 'form-control'})

# class OrderForm(forms.ModelForm):
#     class Meta:
#         model = Orders
#         fields = ['username', 'total_amount', 'payment_mode', 'transaction_id', 'payment_gateway', 'email']