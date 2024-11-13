from django.db import models

class FoodItem(models.Model):
    choices = [
        ('snack', 'Snacks'),
        ('hot_drinks', 'Hot Drinks'),
        ('beverages', 'Beverages'),
        ('lunch', 'Lunch'),
    ]

    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    food_choice = models.CharField(max_length=20, choices=choices, default='snack')
    is_in_stock = models.BooleanField(default=True)
    stock_quantity = models.PositiveIntegerField(default=0)
    image = models.ImageField(upload_to='food_images/', blank=True, null=True)

    def __str__(self):
        return self.name