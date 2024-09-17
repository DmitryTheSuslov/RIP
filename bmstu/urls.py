from django.contrib import admin
from django.urls import path
from bmstu_lab import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('hello/', views.hello),
    path('', views.GetAddresses),
    path('address/<int:id>/', views.GetCard, name="address_url"),
    path('orders/', views.GetOrders)
]
