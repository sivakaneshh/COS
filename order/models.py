from django.db import models
from django.contrib.auth.models import User
from canteen.models import FoodItem



STATUS_CHOICES = (
    ("Pending", "Pending"),
    ("Accepted", "Accepted"),
    ("Packed", "Packed"),
    ("Completed", "Completed"),
)


PAYMENT_CHOICES = (
    ("Cash", "Cash"),
    ("Online", "Online"),
)

# Create your models here.
class Cart(models.Model):
    username = models.ForeignKey(User, on_delete=models.CASCADE)
    food = models.ForeignKey(FoodItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)


class Orders(models.Model):
    # Status choices defined within the Orders model
    STATUS_CHOICES = (
        ("Pending", "Pending"),
        ("Completed", "Completed"),
    )

    PAYMENT_CHOICES = (
        ("Cash", "Cash"),
        ("Online", "Online"),
    )

    username = models.ForeignKey(User, on_delete=models.CASCADE)
    total_amount = models.IntegerField()
    order_datetime = models.DateTimeField(auto_now_add=True)
    payment_mode = models.CharField(max_length=50, choices=PAYMENT_CHOICES)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default="Pending")
    transaction_id = models.CharField(max_length=100)
    payment_gateway = models.CharField(max_length=50)
    email = models.EmailField(max_length=255, blank=True, null=True)


    def __str__(self):
        return f"Order {self.id} by {self.username.username} - Status: {self.status}"
    
class OrderItems(models.Model):
    username = models.ForeignKey(User, on_delete=models.CASCADE) 
    order = models.ForeignKey("Orders", on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    price = models.IntegerField()
    quantity = models.PositiveIntegerField()
    item_total = models.IntegerField()

from django.db import models

class RFID(models.Model):
    name = models.CharField(max_length=100)                     
    roll_number = models.CharField(max_length=20, unique=True)  
    rfid_tag = models.IntegerField(unique=True)                 

    def __str__(self):
        return f"{self.roll_number} - {self.name} - {self.rfid_tag}"
