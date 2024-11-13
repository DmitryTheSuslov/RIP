from .views import *
from django.contrib import admin
from django.urls import path
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

...

schema_view = get_schema_view(
   openapi.Info(
      title="Snippets API",
      default_version='v1',
      description="Test description",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="contact@snippets.local"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
   
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

    path('api/users/update/', private_user), 
    path('api/users/register/', register_user),
    path('api/users/login', login_user),
    path('api/users/logout', logout_user),
    path('api/user/whoami/', whoami, name='user-whoami'),
]
