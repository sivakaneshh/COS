from django.shortcuts import render, redirect
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages


# Check if user is a canteen staff (you can adjust this as per your user roles)
#def is_canteen_staff(user):
#    return user.is_staff  # or use your custom logic if needed


