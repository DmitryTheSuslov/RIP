from rest_framework import permissions
from .models import User
import redis
from django.conf import settings
from django.shortcuts import get_object_or_404
# from .views import session_storage

session_storage = redis.StrictRedis(host=settings.REDIS_HOST, port=settings.REDIS_PORT)


class IsAuth(permissions.BasePermission):
    def has_permission(self, request, view):
        try:
            username = session_storage.get(request.COOKIES["session_id"])
            username = username.decode('utf-8') if username else None
        except:
            return False
        
        # user = User.objects.filter(username=username)
        return username


class IsModerator(permissions.BasePermission):
    def has_permission(self, request, view):
        try:
            username = session_storage.get(request.COOKIES["session_id"])
            username = username.decode('utf-8') if username else None
        except:
            return False
        user = get_object_or_404(User, username=username)
        return user.is_superuser or user.is_staff

# class IsAdmin(permissions.BasePermission):
#     def has_permission(self, request, view):
#         try:
#             username = session_storage.get(request.COOKIES["session_id"])
#             username = username.decode('utf-8')
#         except:
#             return False
        
#         user = get_object_or_404(User, username=username)
#         return user.is_superuser