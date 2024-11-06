from django.contrib.auth.models import User
from django import forms
from canteen.models import FoodItem
from .models import *
class LoginRegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    class Meta:
        model = User
        fields = ('username', 'password')

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