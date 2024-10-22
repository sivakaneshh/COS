from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('add-food/', views.add_food, name='add_food'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
