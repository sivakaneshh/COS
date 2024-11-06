from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('update-cart/<int:f_id>', views.update_cart, name='update-cart'),
    path('cart/', views.cart, name='cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('myorders/', views.my_orders, name='my-orders'),
    path('logout/', views.user_logout, name='logout'),
    path('add-food/', views.add_food, name='add_food'),
    path('canteenside/', views.canteenside, name='canteenside'),
    path('update_order_status/<int:order_id>/', views.update_order_status, name='update_order_status'),
    path('orders/', views.list_orders, name='list_orders'),
    path('buy-now/<int:food_id>/', views.buy_now, name='buy-now'),
    path('clear-completed-orders/', views.clear_completed_orders, name='clear_completed_orders'),
    path('orders/details/<int:order_id>/', views.order_details, name='order-details'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)