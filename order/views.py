from django.shortcuts import render, HttpResponse, HttpResponseRedirect,redirect,get_object_or_404, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from canteen.models import FoodItem
from .models import Cart, Orders, OrderItems
from .forms import LoginRegisterForm
import random
from canteen.forms import FoodItemForm
from canteen.models import FoodItem
from django.contrib.auth.models import Group
from django.http import JsonResponse


# Create your views here.
def index(request):
    food = FoodItem.objects.all()
    name_quantity_of_all_food = []
    if(request.user.is_authenticated):
        cartitems = Cart.objects.filter(username=request.user)
        for f in food:
            find = False
            name_quantity_combo = []
            for item in cartitems:
                if(f.name == item.food.name):
                    name_quantity_combo.append(f.name)
                    name_quantity_combo.append(item.quantity)
                    find = True
                    break
            if(not find):
                name_quantity_combo.append(f.name)
                name_quantity_combo.append('0')
            name_quantity_of_all_food.append(name_quantity_combo)
    return render(request, 'order/index.html', {'food':food, 'cartitems':name_quantity_of_all_food})

def register(request):
    if(request.method == 'GET'):
        form = LoginRegisterForm()
        return render(request, 'order/register.html', {'form':form})
    elif(request.method == 'POST'):
        form = LoginRegisterForm(request.POST)
        un = request.POST.get('username')
        pw = request.POST.get('password')
        if(User.objects.filter(username=un).exists()):
            messages.warning(request, 'User Already Exists, try other unique username')
            return HttpResponseRedirect('/register/')
        else:
            if(form.is_valid()):
                un = form.cleaned_data['username']
                pw = form.cleaned_data['password']
                new_user = User(username=un)
                new_user.set_password(pw)
                new_user.save()
                messages.success(request, 'Account Created Successfully, You can Login Now')
                return HttpResponseRedirect('/login/')

def user_login(request):
    if(request.method == 'GET'):
        form = LoginRegisterForm()
        return render(request, 'order/login.html', {'form':form})
    elif(request.method == 'POST'):
        form = LoginRegisterForm(request.POST)
        un = request.POST.get('username')
        pw = request.POST.get('password')
        if(not User.objects.filter(username=un).exists()):
            messages.warning(request, 'User Does Not Exist or Wrong Password, Try Again')
            return HttpResponseRedirect('/login/')
        else:
            auth_user = authenticate(username=un, password=pw)
            if(auth_user):
                login(request, auth_user)
                return HttpResponseRedirect('/')
            else:
                messages.warning(request, 'User Does Not Exist or Wrong Password, Try Again')
                return HttpResponseRedirect('/login/')

@login_required(login_url='/login/')
def update_cart(request, f_id):
    food = FoodItem.objects.get(id=f_id)
    if(Cart.objects.filter(username = request.user, food=food).exists()):
        old_quantity = Cart.objects.values_list('quantity', flat=True).get(username=request.user, food=food)
        if(request.GET.get('name') == 'increase_cart'):
            updated_quantity = old_quantity + 1
            Cart.objects.filter(username = request.user, food=food).update(quantity = updated_quantity)
        elif(request.GET.get('name') == 'decrease_cart'):
            updated_quantity = old_quantity - 1
            Cart.objects.filter(username = request.user, food=food).update(quantity = updated_quantity)
        elif(request.GET.get('name') == 'delete_cart_item'):
            item_to_delete = Cart.objects.get(username=request.user, food=food)
            item_to_delete.delete()
    else:
        cart_item = Cart(username = request.user, food=food)
        cart_item.save()

    if('cart' in request.META['HTTP_REFERER']):
        return HttpResponseRedirect('/cart/')
    else:
        return HttpResponseRedirect('/')

@login_required(login_url='/login/')
def cart(request):
    cartitems = Cart.objects.filter(username=request.user)
    total_amount = 0
    if(cartitems):
        for item in cartitems:
            sub_total = item.food.price * item.quantity
            total_amount += sub_total
    return render(request, 'order/cart.html', {'cartitems':cartitems, 'total_amount':total_amount})

@login_required(login_url='/login/')
def checkout(request):
    if request.method == 'POST':
        # Determine payment details
        if request.POST.get('paymode') == 'Cash':
            tn_id = 'CASH' + str(random.randint(111111111111111, 999999999999999))
            payment_mode = "Cash"
            payment_gateway = "Cash"
        elif request.POST.get('paymode') == 'Online' and request.POST.get('paygate') == "Paypal":
            tn_id = request.POST.get('tn_id')
            payment_mode = "Online"
            payment_gateway = "Paypal"
        else:
            return HttpResponse('<H1>Invalid Request</H1>')
        
        # Get cart items and create a new order
        cartitems = Cart.objects.filter(username=request.user)
        total_amount = 0
        new_order = Orders(username=request.user, total_amount=total_amount, payment_mode=payment_mode, transaction_id=tn_id, payment_gateway=payment_gateway)
        new_order.save()  # Save the new order to get the `order_id`

        # Add items to the order
        if cartitems:
            for item in cartitems:
                OrderItems(
                    username=request.user,
                    order=new_order,
                    name=item.food.name,
                    price=item.food.price,
                    quantity=item.quantity,
                    item_total=item.food.price * item.quantity
                ).save()

                sub_total = item.food.price * item.quantity
                total_amount += sub_total

            # Update the total amount of the order
            new_order.total_amount = total_amount
            new_order.save()

        # Clear the cart after checkout
        cartitems.delete()

        # Redirect to 'my orders' page with the new `order_id`
        messages.success(request, f'Order placed successfully! Your Order ID is {new_order.id}.')
        return HttpResponseRedirect('/myorders/')
    else:
        return HttpResponse('<H1>Invalid Request</H1>')

@login_required(login_url='/login/')
def my_orders(request):
    orders = Orders.objects.filter(username = request.user).order_by("-order_datetime", "id")
    order_items = OrderItems.objects.filter(username = request.user)
    return render(request, 'order/myorders.html', {'orders':orders, 'order_items':order_items})

def user_logout(request):
    logout(request)
    messages.success(request, 'Logout Successfully')
    return HttpResponseRedirect('/')





from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import FoodItem
from .forms import FoodItemForm

@login_required(login_url='/login/')
def add_food(request):
    # Check if the user belongs to the "canteen" group
    if request.user.groups.filter(name='canteen').exists():

        # Handle food deletion
        if request.method == 'POST' and 'delete_food' in request.POST:
            food_id = request.POST.get('food_id')
            food_item_to_delete = get_object_or_404(FoodItem, id=food_id)
            food_item_to_delete.delete()
            messages.success(request, 'Food item deleted successfully!')
            return redirect('add_food')  # Redirect back after deletion

        # Handle adding new food
        if request.method == 'POST' and 'add_food' in request.POST:
            form = FoodItemForm(request.POST, request.FILES)
            if form.is_valid():
                form.save()
                messages.success(request, 'Food item added successfully!')
                return redirect('add_food')  # Redirect back after adding

        # Handle updating stock
        elif request.method == 'POST' and 'update_stock' in request.POST:
            food_id = request.POST.get('food_id')
            new_stock = request.POST.get('new_stock')
            food_item = get_object_or_404(FoodItem, id=food_id)
            
            # Update the stock quantity
            try:
                food_item.stock_quantity = int(new_stock)
                food_item.save()
                messages.success(request, 'Stock updated successfully!')
            except ValueError:
                messages.error(request, 'Invalid stock quantity. Please enter a valid number.')

            return redirect('add_food')  # Redirect back after stock update

        else:
            form = FoodItemForm()

        # Display existing food items for reference
        food_items = FoodItem.objects.all()

        return render(request, 'order/add_food.html', {
            'form': form,
            'food_items': food_items
        })

    # If the user is not part of the "canteen" group, deny access
    else:
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('/')



@login_required(login_url='/login/')
def canteenside(request):
    # Check if the user belongs to the "canteen" group
    if request.user.groups.filter(name='canteen').exists():
        return render(request, 'order/canteenside.html')
    else:
        # If not in the "canteen" group, show a permission denied message or redirect
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('/')
    

def update_order_status(request, order_id):
    order = get_object_or_404(Orders, id=order_id)

    if request.method == 'POST':
        new_status = request.POST.get('status')

        # Validate the new status against the choices defined in the model
        if new_status in dict(Orders.STATUS_CHOICES):  # Use the top-level STATUS_CHOICES
            order.status = new_status
            order.save()
            messages.success(request, f"Order {order_id} status updated successfully!")
            return redirect('canteenside')
        else:
            messages.error(request, "Invalid status selected.")
            return redirect('update_order_status', order_id=order_id)

    
    return render(request, 'order/update_status.html', {'order': order, 'order_id': order.id})

@login_required(login_url='/login/')
def list_orders(request):
    if request.method == 'POST':
        # Handling the form submission to update the order status
        order_id = request.POST.get('order_id')  # Get the order ID from the form
        new_status = request.POST.get('status')  # Get the new status from the form

        try:
            # Fetch the order object by its ID
            order = Orders.objects.get(id=order_id)
            # Update the order status
            order.status = new_status
            order.save()  # Save the updated status to the database

            # Show success message after updating
            messages.success(request, f"Order {order_id} status updated successfully.")
        except Orders.DoesNotExist:
            # Handle case where order is not found
            messages.error(request, "Order not found.")
        
        # Redirect back to the same page to avoid re-posting the form
        return redirect('list_orders')

    # Fetch all orders to display in the template
    orders = Orders.objects.all()

    # Debugging line to print orders in the console
    print(f"Retrieved orders: {orders}")

    # Pass the list of orders to the template
    return render(request, 'order/list_orders.html', {'orders': orders})

def buy_now(request, food_id):
    food_item = get_object_or_404(FoodItem, id=food_id)

    # Check if the item is already in the cart
    cart_item, created = Cart.objects.get_or_create(
        username=request.user,
        food=food_item,
        defaults={'quantity': 1}  # If new, set quantity to 1
    )
    
    if not created:
        # If it already exists, update the quantity to 1
        cart_item.quantity = 1
        cart_item.save()

    # Redirect to the cart page for review or checkout
    return redirect('cart')

def clear_completed_orders(request):
    if request.method == 'DELETE':
        Orders.objects.filter(status='Completed').delete()
        return JsonResponse({'message': 'Completed orders cleared successfully.'}, status=200)
    return JsonResponse({'error': 'Invalid request method.'}, status=400)