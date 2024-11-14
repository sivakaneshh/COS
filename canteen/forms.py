from django import forms
from .models import FoodItem

# Form to Add/Update Food Items (including image upload)
class FoodItemForm(forms.ModelForm):
    class Meta:
        model = FoodItem
        fields = ['name', 'price', 'image', 'food_choice' ]  # Include 'image' field to allow image uploads
    
    def __init__(self, *args, **kwargs):
        super(FoodItemForm, self).__init__(*args, **kwargs)
        self.fields['name'].widget.attrs.update({'class': 'form-control'})
        self.fields['price'].widget.attrs.update({'class': 'form-control'})
        self.fields['food_choice'].widget.attrs.update({'class':"form-control"})
        self.fields['image'].widget.attrs.update({'class': 'form-control'})



    