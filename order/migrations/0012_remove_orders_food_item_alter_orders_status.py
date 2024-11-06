# Generated by Django 4.2 on 2024-11-06 07:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0011_orders_food_item_alter_orders_status'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='orders',
            name='food_item',
        ),
        migrations.AlterField(
            model_name='orders',
            name='status',
            field=models.CharField(choices=[('Pending', 'Pending'), ('Accepted', 'Accepted'), ('Cooking', 'Cooking'), ('Packed', 'Packed'), ('Completed', 'Completed')], default='Pending', max_length=50),
        ),
    ]