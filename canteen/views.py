from django.shortcuts import render, redirect
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import FoodItemForm
from .models import FoodItem

# Check if user is a canteen staff (you can adjust this as per your user roles)
#def is_canteen_staff(user):
#    return user.is_staff  # or use your custom logic if needed

@login_required(login_url='/login/')
def add_food(request):
    if request.method == 'POST':
        form = FoodItemForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Food item added successfully!')
            return redirect('add_food')  # Redirect back to the add food page after submission
    else:
        form = FoodItemForm()

    # You can also display existing food items for reference
    food_items = FoodItem.objects.all()
    
    return render(request, 'canteen/add_food.html', {'form': form, 'food_items': food_items})
