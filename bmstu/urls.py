from django.contrib import admin
from django.urls import path
from bmstu_lab import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index),
    path('address/<int:id>/', views.address_details, name="address_url"),
    path('address/<int:id>/add/', views.add_address),
    path('fixation/<int:id>/', views.fixation_details),
    path('fixation/<int:id>/delete/', views.del_fixation)
]
