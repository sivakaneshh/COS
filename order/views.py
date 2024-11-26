from django.shortcuts import render, redirect, get_object_or_404, HttpResponseRedirect, HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User, Group
from django.http import JsonResponse
from django.db import transaction
import random
from django.views import View
from canteen.models import FoodItem
from .models import Cart, Orders, OrderItems,RFID,Completed
from .forms import LoginRegisterForm
from canteen.forms import FoodItemForm

from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.decorators import method_decorator

from openpyxl import Workbook
from django.http import HttpResponse
from django.utils.timezone import now


def index(request):
    food_items = FoodItem.objects.all()
    cart_summary = []

    if request.user.is_authenticated:
        cart_items = Cart.objects.filter(username=request.user)
        for food in food_items:
            quantity = 0
            for item in cart_items:
                if food.name == item.food.name:
                    quantity = item.quantity
                    break
            cart_summary.append({'name': food.name, 'quantity': quantity})

    return render(request, 'order/index.html', {'food': food_items, 'cartitems': cart_summary})


def register(request):
    if request.method == 'GET':
        form = LoginRegisterForm()
        return render(request, 'order/register.html', {'form': form})
    
    elif request.method == 'POST':
        form = LoginRegisterForm(request.POST)
        if form.is_valid():
            roll_number = form.cleaned_data['username']
            password = form.cleaned_data['password']

            rfid_obj = RFID.objects.get(roll_number=roll_number)
            new_user = User.objects.create_user(username=rfid_obj.roll_number, password=password)
            new_user.save()

            messages.success(request, 'Account created successfully. You can now log in.')
            return redirect('login')
        else:
            messages.error(request, 'Invalid form submission. Please try again.')
            return redirect('register')


def user_login(request):
    if request.method == 'GET':
        form = LoginRegisterForm()
        return render(request, 'order/login.html', {'form': form})

    elif request.method == 'POST':
        form = LoginRegisterForm(request.POST)
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username=username, password=password)
        if user:
            login(request, user)
            return redirect('index')
        else:
            messages.warning(request, 'Invalid username or password. Please try again.')
            return redirect('login')


@login_required(login_url='login')
def update_cart(request, f_id):
    # Get the food item or return 404 if it doesn't exist
    food = get_object_or_404(FoodItem, id=f_id)
    
    # Check if a cart item exists for this user and food item
    cart_item, created = Cart.objects.get_or_create(username=request.user, food=food, defaults={'quantity': 1})
    
    # If the cart item was newly created, we can skip the update actions
    if not created:
        # Retrieve the requested action
        action = request.GET.get('name')
        
        if action == 'increase_cart':
            cart_item.quantity += 1  # Increase quantity
            cart_item.save()
        
        elif action == 'decrease_cart':
            if cart_item.quantity > 1:
                cart_item.quantity -= 1  # Decrease quantity but ensure it's not below 1
                cart_item.save()
            else:
                cart_item.delete()  # If quantity is 1, delete the item to remove it from cart
        
        elif action == 'delete_cart_item':
            cart_item.delete()  # Remove the item from the cart

    # Redirect based on the referrer
    if 'cart' in request.META.get('HTTP_REFERER', ''):
        return HttpResponseRedirect('/cart/')
    else:
        return HttpResponseRedirect('/')

@login_required(login_url='login')
def cart(request):
    cart_items = Cart.objects.filter(username=request.user)
    total_amount = sum(item.food.price * item.quantity for item in cart_items)
    return render(request, 'order/cart.html', {'cartitems': cart_items, 'total_amount': total_amount})


@transaction.atomic
def checkout(request):
    if request.method == 'POST':
        payment_mode = request.POST.get('paymode')
        payment_gateway = request.POST.get('paygate', 'Cash')
        tn_id = request.POST.get('tn_id', f'CASH{random.randint(111111111111111, 999999999999999)}')

        if payment_mode not in ['Cash', 'Online'] or (payment_mode == 'Online' and payment_gateway != 'Paypal'):
            return HttpResponse('<h1>Invalid Request</h1>')

        cart_items = Cart.objects.filter(username=request.user)
        if not cart_items.exists():
            messages.error(request, 'Your cart is empty.')
            return redirect('cart')

        new_order = Orders.objects.create(
            username=request.user,
            total_amount=0,
            payment_mode=payment_mode,
            transaction_id=tn_id,
            payment_gateway=payment_gateway
        )

        total_amount = 0
        for item in cart_items:
            if item.food.stock_quantity < item.quantity:
                messages.error(request, f'Not enough stock for {item.food.name}.')
                return redirect('cart')

            item.food.stock_quantity -= item.quantity
            item.food.save()

            OrderItems.objects.create(
                username=request.user,
                order=new_order,
                name=item.food.name,
                price=item.food.price,
                quantity=item.quantity,
                item_total=item.food.price * item.quantity
            )

            total_amount += item.food.price * item.quantity

        new_order.total_amount = total_amount
        new_order.save()
        cart_items.delete()

        messages.success(request, f'Order placed successfully! Your Order ID is {new_order.id}.')
        return redirect('/myorders/')

    return HttpResponse('<h1>Invalid Request</h1>')


@login_required(login_url='login')
def my_orders(request):
    orders = Orders.objects.filter(username=request.user).order_by("-order_datetime", "id")
    order_items = OrderItems.objects.filter(username=request.user)
    return render(request, 'order/myorders.html', {'orders': orders, 'order_items': order_items})


def user_logout(request):
    logout(request)
    messages.success(request, 'Logged out successfully.')
    return redirect('index')


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

        #Handle updating stock
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


@login_required(login_url='login')
def canteenside(request):
    if request.user.groups.filter(name='canteen').exists():
        return render(request, 'order/canteenside.html')

    messages.error(request, 'You do not have permission to access this page.')
    return redirect('index')


# def update_order_status(request, order_id):
#     order = get_object_or_404(Orders, id=order_id)

#     if request.method == 'POST':
#         new_status = request.POST.get('status')

#         if new_status in dict(Orders.STATUS_CHOICES):
#             order.status = new_status
#             order.save()
#             messages.success(request, f'Order {order_id} status updated successfully.')
#             return redirect('canteenside')

#         messages.error(request, 'Invalid status selected.')
#         return redirect('update_order_status', order_id=order_id)

#     return render(request, 'order/update_status.html', {'order': order})


@login_required(login_url='login')
def buy_now(request, food_id):
    food_item = get_object_or_404(FoodItem, id=food_id)

    cart_item, created = Cart.objects.get_or_create(
        username=request.user,
        food=food_item,
        defaults={'quantity': 1}
    )
    if not created:
        cart_item.quantity = 1
        cart_item.save()

    return redirect('cart')


def order_details(request, order_id):
    order = get_object_or_404(Orders, id=order_id)
    order_items = OrderItems.objects.filter(order=order)
    
    # Build data to send back as JSON
    data = {
        'order_id': order.id,
        'total_amount': order.total_amount,
        'payment_mode': order.payment_mode,
        'items': [
            {
                'name': item.name,
                'price': item.price,
                'quantity': item.quantity,
            }
            for item in order_items
        ]
    }
    
    return JsonResponse(data)

def clear_completed_orders(request):
    if request.method == 'DELETE':
        Orders.objects.filter(status='Completed').delete()
        return JsonResponse({'message': 'Completed orders cleared successfully.'}, status=200)

    return JsonResponse({'error': 'Invalid request method.'}, status=400)

@login_required(login_url='login')
def list_orders(request):
    if request.method == 'POST':
        order_id = request.POST.get('order_id')
        new_status = request.POST.get('status')

        try:
            # Update the order status
            order = Orders.objects.get(id=order_id)
            order.status = new_status
            order.save()
            messages.success(request, f'Order {order_id} status updated successfully.')
        except Orders.DoesNotExist:
            messages.error(request, 'Order not found.')

        return redirect('list_orders')

    # Fetch all orders with related user data
    orders = Orders.objects.select_related('username').all()

    # Create a mapping of roll numbers to RFID names
    rfid_map = {rfid.roll_number: rfid.name for rfid in RFID.objects.all()}

    # Add the RFID name to each order dynamically if available
    for order in orders:
        user_roll_number = order.username.username  # Assuming `username` field on `User` is the roll number in `RFID`
        # Set `rfid_name` to the matched RFID name or fallback to the `username` if no match is found
        order.rfid_name = rfid_map.get(user_roll_number, order.username.username)

    # Fetch all available food items (regardless of whether they are ordered or not)
    food_items = FoodItem.objects.all()

    # Pass orders and food items to the template
    return render(request, 'order/list_orders.html', {
        'orders': orders,
        'food_items': food_items,  # All food items (not just the ordered ones)
    })



@login_required(login_url='/login/')
def rfid_punch_view(request):
    if request.method == 'POST':
        # Handling RFID punch form submission
        if 'rfid_tag' in request.POST:
            rfid_tag = request.POST.get('rfid_tag')
            try:
                # Get the RFID object by RFID tag
                rfid_obj = RFID.objects.get(rfid_tag=rfid_tag)
                # Retrieve the user associated with the RFID roll number
                user = User.objects.get(username=rfid_obj.roll_number)

                # Check for any pending orders for the user
                pending_orders = Orders.objects.filter(username=user, status='Pending')
                if pending_orders.exists():
                    for order in pending_orders:
                        order.status = 'Completed'
                        order.save()
                    messages.success(request, 'Orders marked as completed.')
                else:
                    messages.info(request, 'No pending orders found for this user.')

            except (RFID.DoesNotExist, User.DoesNotExist):
                messages.error(request, 'Invalid RFID tag.')
            return redirect('punch')

        # Handling individual order status update form submission
        elif 'order_id' in request.POST:
            order_id = request.POST.get('order_id')
            new_status = request.POST.get('status')

            try:
                order = Orders.objects.get(id=order_id)
                order.status = new_status
                order.save()
                messages.success(request, f'Order {order_id} status updated successfully.')
            except Orders.DoesNotExist:
                messages.error(request, 'Order not found.')
            return redirect('punch')

    # For GET requests: Retrieve orders and render the template with RFID names included
    orders = Orders.objects.select_related('username').all()

    # Create a mapping of roll numbers to RFID names for display purposes
    rfid_map = {rfid.roll_number: rfid.name for rfid in RFID.objects.all()}

    # Attach `rfid_name` to each order for use in the template
    for order in orders:
        user_roll_number = order.username.username  # Assuming `username` field on `User` is the roll number in `RFID`
        # Set `rfid_name` to the matched RFID name or fallback to the `username` if no match is found
        order.rfid_name = rfid_map.get(user_roll_number, order.username.username)

    return render(request, 'order/list_orders.html', {'orders': orders})


def completed_orders(request):
    """
    View to display the completed orders page.
    """
    # Fetch all orders with status 'Completed'
    orders = Orders.objects.filter(status='Completed')
    orders = Orders.objects.select_related('username').all()
    # Create a mapping of roll numbers to RFID names
    rfid_map = {rfid.roll_number: rfid.name for rfid in RFID.objects.all()}

    # Add the RFID name to each order dynamically if available
    for order in orders:
        user_roll_number = order.username.username  # Assuming `username` field on `User` is the roll number in `RFID`
        # Set `rfid_name` to the matched RFID name or fallback to the `username` if no match is found
        order.rfid_name = rfid_map.get(user_roll_number, order.username.username)

    
    # Pass orders to the template
    return render(request, 'order/completed.html', {'orders': orders})



def download_summary(request):

    # Get the current date
    today = now().date()

    # Fetch completed items for the day
    completed_items = Completed.objects.filter(status="Completed")

    # Create a workbook and active worksheet
    wb = Workbook()
    ws = wb.active
    ws.title = f"Summary_{today}"

    # Write the header row
    headers = [ 'Food Name', 'Quantity', 'Price', 'Item Total', 'Payment Type']
    ws.append(headers)

    # Write data rows
    for item in completed_items:
        ws.append([
           
            item.food_name,  # Food Name
            item.food_quantity,  # Quantity
            item.food_price,  # Price per item
            item.food_quantity * item.food_price,  # Item Total
            item.payment_type,  # Payment Type
            #item.order.order_datetime.strftime('%Y-%m-%d %H:%M:%S'),  # Order Time
        ])

    # Set the response for downloading the Excel file
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    filename = f"sold_items_summary_{today}.xlsx"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    # Save the workbook to the response
    wb.save(response)

    return response


from django.shortcuts import redirect

def transfer_completed_orders(request):
    """
    Transfers all items from orders marked as 'Completed' to the Completed model.
    """
    if request.method == 'POST':
        # Fetch all orders with the status 'Completed'
        completed_orders = Orders.objects.filter(status='Completed')
        print(f"Found {completed_orders.count()} completed orders.")  # Debugging output
        
        for order in completed_orders:
            # Fetch related order items for each completed order
            order_items = OrderItems.objects.filter(order=order)
            #print(f"Processing Order {order.id} with {order_items.count()} items.")  # Debugging output

            for item in order_items:
                # Check if entry exists and update quantity, or create new entry
                completed_item, created = Completed.objects.get_or_create(
                    order=order,  # Link to the order
                    food_name=item.name,
                    defaults={
                        'food_price': item.price,
                        'food_quantity': item.quantity,
                        'status': order.status,
                        'payment_type': order.payment_mode
                    }
                )
                
                if not created:
                    # If entry exists, update the quantity
                    completed_item.food_quantity += item.quantity
                    completed_item.save()

        # Redirect to the previous page or a specific page after transfer
        return redirect(request.META.get('HTTP_REFERER', '/'))  # Redirects back to the referring page

    # Handle non-POST requests
    return redirect(request.META.get('HTTP_REFERER', '/'))  # Also redirect in case of invalid request method
