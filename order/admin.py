from django.contrib import admin
from .models import Cart, Orders, OrderItems,RFID

# Register your models here.
@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'food', 'quantity')

@admin.register(Orders)
class OrdersAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'total_amount', 'order_datetime', 'payment_mode', 'status', 'transaction_id', 'payment_gateway')

@admin.register(OrderItems)
class OrderItemsAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'order', 'name', 'price', 'quantity', 'item_total')
    
@admin.register(RFID)
class RFIDAdmin(admin.ModelAdmin):
    list_display = ('roll_number', 'name', 'rfid_tag')  # Columns to display
    search_fields = ('roll_number', 'name')  # Add search functionality