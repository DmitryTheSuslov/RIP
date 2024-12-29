from rest_framework.response import Response
from rest_framework import status
from .serializers import *
from .models import *
import random
from datetime import datetime, timedelta, date

# Генерируем случайную дату
import random
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes, authentication_classes
# from .miniof import *
import logging
from django.contrib.auth import authenticate, login, logout
from rest_framework.permissions import IsAuthenticated
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
import datetime
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets
from django.http import HttpResponse
from rest_framework.permissions import AllowAny
from django.views.decorators.csrf import csrf_exempt
from rest_framework import permissions
import uuid
from django.conf import settings
from .permissions import *
from django.db.models import Min, Max



session_storage = redis.StrictRedis(host=settings.REDIS_HOST, port=settings.REDIS_PORT)

def GetDraftFix(request, id=None):
    """ПОЛУЧЕНИЕ ЧЕРНОВИКА ЗАЯВКИ"""
    session_id = request.COOKIES.get("session_id")
    if not session_id:
        return None  # возвращаем None, если session_id отсутствует

    username = session_storage.get(session_id)
    if not username:
        return None  # возвращаем None, если пользователь не найден в сессии

    username = username.decode('utf-8')
    try:
        current_user = User.objects.get(username=username)
    except User.DoesNotExist:
        return None  # возвращаем None, если пользователь не найден в базе данных

    if id is not None:
        return Fixation.objects.filter(owner=current_user, fixation_id=id).first() 
    else:
        return Fixation.objects.filter(owner=current_user, status=1).first() 


# def GetDraftFix(user):
#     if Fixation.objects.filter(owner=user, status=1).exists():
#         return Fixation.objects.filter(owner=user, status=1).first()
#     return None

def GetUser():
    try:
        username = session_storage.get(request.COOKIES["session_id"])
        username = username.decode('utf-8') 
    except:
        username = ''
    return User.objects.filter(is_superuser=False).first()

def get_moderator():
    return User.objects.filter(is_superuser=True).first()

def GetFix(id):
    draft_booking = GetDraftFix(id)
    fixation_addresses = AddressFixation.objects.filter(fixation=draft_booking)
    addresses = []
    for item in fixation_addresses:
        address = {
            'info': Address.objects.get(address_id=item.address),  
            'value': item.value if item.value else ''
        }
        addresses.append(address)
    return addresses

# ADDRESSES

@api_view(["GET"])
def search_addresses(request):
    # draft = GetDraftFix()
    query = request.query_params.get("name", "")

    draft = GetDraftFix(request) if request.COOKIES.get("session_id") else None
    draft_count = AddressFixation.objects.filter(fixation=draft.fixation_id).count() if draft else None

    addresses = Address.objects.filter(status='active', address_name__icontains=query)
    serializer = AddressSerializer(addresses, many=True)
    response = {    
        "addresses" : serializer.data,
        "draft_fixation" : draft.fixation_id if draft else None,
        "addresses_count" : draft_count
    }
    return Response(response)

#2
@api_view(["GET"])
def get_address_by_id(request, address_id):
    if not Address.objects.filter(address_id=address_id, status='active').exists():
        return Response(status=status.HTTP_404_NOT_FOUND)
    address = Address.objects.get(address_id=address_id)
    serializer = AddressSerializer(address, many=False)
    return Response(serializer.data)

#3
@swagger_auto_schema(method='post', request_body=AddressSerializer)
@api_view(["POST"])
@permission_classes([IsModerator])
def create_address(request):
    address = Address.objects.create()
    address.address_name = request.data['address_name']
    address.save()
    addresses = Address.objects.filter(status='active')
    serializer = AddressSerializer(addresses, many=True)
    return Response(serializer.data)

#4
@swagger_auto_schema(method='put', request_body=AddressSerializer)
@api_view(["PUT"])
@permission_classes([IsModerator])
def update_address(request, address_id):
    if not Address.objects.filter(address_id=address_id, status='active').exists():
        return Response(status=status.HTTP_404_NOT_FOUND)
    address = Address.objects.get(address_id=address_id)
    name = request.data.get("name")
    if name is not None:
        address.address_name = name
        address.save()
    area = request.data.get("area")
    if area is not None:
        address.area = area
        address.save()
    serializer = AddressSerializer(address, data=request.data, many=False, partial=True)
    if serializer.is_valid():
        serializer.save()
    return Response(serializer.data)

#5
@api_view(["DELETE"])
@permission_classes([IsModerator])
def delete_address(request, address_id):
    if not Address.objects.filter(address_id=address_id, status='active').exists():
        return Response(status=status.HTTP_404_NOT_FOUND)
    address = Address.objects.get(address_id=address_id)
    address.status = 'inactive'
    address.save()
    addresses = Address.objects.filter(status='active')
    serializer = AddressSerializer(addresses, many=True)
    return Response(serializer.data)

#6
@swagger_auto_schema(method='post', request_body=FixationsSerializer)
@api_view(["POST"])
@permission_classes([IsAuth])
def add_address_to_fix(request, address_id):
    try:
        if not Address.objects.filter(address_id=address_id).exists():
            return Response(status=status.HTTP_404_NOT_FOUND)
        address = Address.objects.get(address_id=address_id)
        draft_booking = GetDraftFix(request)
        if draft_booking is None:
            draft_booking = Fixation.objects.create()
            username = session_storage.get(request.COOKIES["session_id"])
            username = username.decode('utf-8')
            user = User.objects.get(username=username)
            draft_booking.owner = user
            draft_booking.created_at = timezone.now()
            draft_booking.save()
        if AddressFixation.objects.filter(fixation=draft_booking, address=address).exists():
            return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
        item = AddressFixation.objects.create()
        item.fixation = draft_booking
        item.address = address
        item.save()
        serializer = FixationsSerializer(draft_booking, many=False)
        return Response(serializer.data)
    except:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

#7
@swagger_auto_schema(method='post', request_body=AddressSerializer)
@api_view(["POST"])
@permission_classes([IsModerator])
def update_address_image(request, address_id):
    if not Address.objects.filter(address_id=address_id, status='active').exists():
        return Response(status=status.HTTP_404_NOT_FOUND)
    address = Address.objects.get(address_id=address_id)
    image = request.data.get("image")
    if image is not None:
        address.photo = image
        address.save()
    serializer = AddressSerializer(address)
    return Response(serializer.data)

# FIXATIONS

#8
@api_view(["GET"])
@permission_classes([IsAuth])
def fixations_list(request):
    date_formation_start = request.GET.get("date_formation_start")
    date_formation_end = request.GET.get("date_formation_end")

    try:
        username = session_storage.get(request.COOKIES["session_id"]).decode('utf-8')
    except:
        return Response(status=status.HTTP_401_UNAUTHORIZED)

    if User.objects.filter(username = username).exists():
        user = get_object_or_404(User, username = username)
        if user.is_staff or user.is_superuser:
            fixations = Fixation.objects.all()
        else:
            fixations = Fixation.objects.filter(owner=user).exclude(status=5)
    serializer = FixationsSerializer(fixations, many=True)
    return Response(serializer.data)

#9
@api_view(["GET"])  
@permission_classes([IsAuth])
def get_fix_by_id(request, fix_id):
    if not Fixation.objects.filter(fixation_id=fix_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)
    fixation = Fixation.objects.get(fixation_id=fix_id)
    serializer = FixationsSerializer(fixation, many=False)
    return Response(serializer.data)

#10
@swagger_auto_schema(method='put', request_body=FixationsSerializer)
@api_view(["PUT"])
@permission_classes([IsAuth])
def update_fix_by_id(request, fix_id):
    if not Fixation.objects.filter(fixation_id=fix_id).exclude(status=5).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)
    fixation = Fixation.objects.get(fixation_id=fix_id)
    month = request.data.get("month")
    if month is not None:
        fixation.month = month
        fixation.save()
    serializer = FixationsSerializer(fixation, data=request.data, many=False, partial=True)
    if serializer.is_valid():
        serializer.save()
    return Response(serializer.data)

#11
@swagger_auto_schema(method='put', request_body=FixationsSerializer)
@api_view(["PUT"])
@permission_classes([IsAuth])
def update_status_user(request, fix_id):
    username = session_storage.get(request.COOKIES["session_id"]).decode('utf-8')
    user = get_object_or_404(User, username = username)
    if not Fixation.objects.filter(fixation_id=fix_id).exclude(status=5).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)
    fixation = Fixation.objects.get(fixation_id=fix_id)
    if fixation.owner != user:
        return Response(status=status.HTTP_403_FORBIDDEN)
    if fixation.status == 1:
        mms = AddressFixation.objects.filter(fixation_id=fix_id).all()
        for mm in mms:
            start_date = date.today().replace(day=1, month=1).toordinal()
            end_date = date.today().toordinal()
            random_day = date.fromordinal(random.randint(start_date, end_date)).replace(year=2025)
            mm.pay_date = random_day
            mm.save()
        fixation.status = 2
        fixation.submitted_at = timezone.now()
        fixation.save()
        serializer = FixationsSerializer(fixation, many=False)
        return Response(serializer.data)
    else:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
    
#12
@swagger_auto_schema(method='put', request_body=FixationsSerializer)
@api_view(["PUT"])
# @permission_classes([IsModerator])
def update_status_admin(request, fix_id):
    if not Fixation.objects.filter(fixation_id=fix_id).exclude(status=5).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)
    stat = request.data["status"]
    if int(stat) not in [3, 4]:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
    fixation = Fixation.objects.get(fixation_id=fix_id)
    if fixation.status == 2:
        fixation.completed_at = timezone.now()
        fixation.status = 3 #stat
        fixation.moderator = get_moderator()
        fixation.save()
        mms = AddressFixation.objects.filter(fixation_id=fix_id).all()
        for mm in mms:
            start_date = date.today().replace(day=1, month=1, year=2025).toordinal()
            end_date = date.today().toordinal()
            random_day = date.fromordinal(random.randint(start_date, end_date))
            mm.pay_date = random_day
            mm.save()
        serializer = FixationsSerializer(fixation, many=False)
        return Response(serializer.data)
    else: 
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
#13
@api_view(["DELETE"])
@permission_classes([IsAuth])
def delete_fix(request, fix_id):
    if not Fixation.objects.filter(fixation_id=fix_id).exclude(status=5).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)
    fixation = Fixation.objects.get(fixation_id=fix_id)
    # if fixation.status != 1:
    #     return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
    fixation.status = 5
    fixation.submitted_at = timezone.now()
    fixation.save()
    serializer = FixationsSerializer(fixation, many=False)
    return Response(serializer.data)


#M-M

#14
@swagger_auto_schema(method='put', request_body=AddressFixationSerializer)
@api_view(["PUT"])
@permission_classes([IsAuth])
def update_address_in_fix(request, fix_id, address_id):
    if not AddressFixation.objects.filter(fixation_id=fix_id, address_id=address_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)
    item = AddressFixation.objects.get(fixation_id=fix_id, address_id=address_id)
    value = request.data.get("value")
    if value:
        item.value = value
    serializer = AddressFixationSerializer(item, data=request.data, many=False, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#15
@api_view(["DELETE"])
@permission_classes([IsAuth])
def delete_address_from_fix(request, fix_id, address_id):
    if not AddressFixation.objects.filter(fixation_id=fix_id, address_id=address_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)
    item = AddressFixation.objects.get(fixation_id=fix_id, address_id=address_id)
    item.delete()
    fixation = Fixation.objects.get(fixation_id=fix_id)
    serializer = FixationsSerializer(fixation, many=False)
    addresses = serializer.data["addresses"]
    if not len(addresses):
        return Response(status=status.HTTP_204_NO_CONTENT)
    return Response(addresses)


#USERS

@swagger_auto_schema(method='post', request_body=UserRegisterSerializer)
@api_view(["POST"])
def register_user(request, format=None): 
    try:
        if request.COOKIES["session_id"] is not None:
            return Response({'status': 'Уже в системе'}, status=status.HTTP_403_FORBIDDEN)
    except:
        if User.objects.filter(username = request.data['username']).exists(): 
            return Response({'status': 'Exist'}, status=400)
        serializer = UserRegisterSerializer(data=request.data) 
        if not serializer.is_valid():
            return Response(status=status.HTTP_400_BAD_REQUEST)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)

@swagger_auto_schema(method='post', request_body=UserLoginSerializer)
@api_view(["POST"])
def login_user(request):
    try:
        if request.COOKIES["session_id"] is not None:
            return Response({'status': 'Уже в системе'}, status=status.HTTP_403_FORBIDDEN)
    except:
        username = str(request.data["username"]) 
        password = request.data["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            random_key = str(uuid.uuid4()) 
            session_storage.set(random_key, username)
            response = Response({'status': f'{username} успешно вошел в систему'})
            response.set_cookie("session_id", random_key)

            return response
        else:
            return HttpResponse("{'status': 'error', 'error': 'login failed'}")
    
@permission_classes([IsAuth])
@api_view(["POST"])
def logout_user(request):
    try:
        username = session_storage.get(request.COOKIES["session_id"])
        username = username.decode('utf-8')
        logout(request._request)
        response = Response({'Message': f'{username} вышел из системы'})
        response.delete_cookie('session_id')
        return response
    except:
        return Response({"Message":"Нет авторизованных пользователей"})
    
@swagger_auto_schema(method='put', request_body=UserSerializer)
@permission_classes([IsAuth])
@api_view(["PUT"])
def private_user(request):
    try:
        username = session_storage.get(request.COOKIES["session_id"])
        username = username.decode('utf-8')
    except:
        return Response({"Message":"Нет авторизованных пользователей"})
    
    if not User.objects.filter(username = username).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    user = get_object_or_404(User, username = username)

    serializer = UserSerializer(user, data=request.data, partial=True)
    if not serializer.is_valid():
        return Response(status=status.HTTP_409_CONFLICT)

    serializer.save()

    return Response(serializer.data, status=status.HTTP_200_OK)

@permission_classes([IsAuth])
@api_view(["GET"])
def whoami(request):
    try:
        username = session_storage.get(request.COOKIES["session_id"])
        username = username.decode('utf-8')
    except:
        return Response({"Message":"Нет авторизованных пользователей"})
    
    user = get_object_or_404(User, username = username)
    serializer = UserSerializer(user)
    return Response(serializer.data)