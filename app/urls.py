"""
URL configuration for lab3 project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from .views import *
from django.contrib import admin
from django.urls import path

urlpatterns = [
    path("admin/", admin.site.urls),
   
    path('api/addresses/search/', search_addresses),
    path('api/addresses/<int:address_id>/', get_address_by_id),  
    path('api/addresses/create/', create_address), 
    path('api/addresses/<int:address_id>/update/', update_address),  
    path('api/addresses/<int:address_id>/delete/', delete_address), 
    path('api/addresses/<int:address_id>/add_to_fix/', add_address_to_fix),  
    path('api/addresses/<int:address_id>/update_image/', update_address_image), 
  
    path('api/fixations/search/', fixations_list),  
    path('api/fixations/<int:fix_id>/', get_fix_by_id),  
    path('api/fixations/<int:fix_id>/update/', update_fix_by_id),  
    path('api/fixations/<int:fix_id>/update_status_user/', update_status_user),  
    path('api/fixations/<int:fix_id>/update_status_admin/', update_status_admin),  
    path('api/fixations/<int:fix_id>/delete/', delete_fix),  
    path('api/fixations/<int:fix_id>/update_address/<int:address_id>/', update_address_in_fix),  
    path('api/fixations/<int:fix_id>/delete_address/<int:address_id>/', delete_address_from_fix), 
    path('api/users/<int:user_id>/update/', update_user), 
    path('api/users/register/', register)
]
