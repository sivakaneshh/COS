from django import forms
from .models import FoodItem

# Form to Add/Update Food Items (including image upload)
class FoodItemForm(forms.ModelForm):
    class Meta:
        model = FoodItem
        fields = ['name', 'price', 'image', 'food_choice' ]  # Include 'image' field to allow image uploads
    
    def __init__(self, *args, **kwargs):
        super(FoodItemForm, self).__init__(*args, **kwargs)
        for field in ['name', 'price', 'food_choice', 'image']:
            self.fields[field].widget.attrs.update({'class': 'form-control'})



    
