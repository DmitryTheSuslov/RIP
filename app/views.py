import requests
from django.http import HttpResponse
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response 
from .serializers import *

def GetDraftFix(id=None):
    current_user = GetUser()
    if id is not None:
        return Fixation.objects.filter(owner=current_user.id, fixation_id=id).first() 
    else:
        return Fixation.objects.filter(owner=current_user.id, status=1).first() 

def GetUser():
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

#1
@api_view(["GET"])
def search_addresses(request):
    draft = GetDraftFix()
    addresses = AddressFixation.objects.filter(fixation=draft)
    serializer = AddressSerializer(addresses, many=True)
    response = {    
        "addresses" : serializer.data,
        "draft_fixation" : draft.fixation_id if draft else None,
        "addresses_count" : addresses.count()
    }
    return Response(response)

#2
@api_view(["GET"])
def get_address_by_id(request, address_id):
    if not Address.objects.filter(address_id=address_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)
    address = Address.objects.get(address_id=address_id)
    serializer = AddressSerializer(address, many=False)
    return Response(serializer.data)

#3
@api_view(["POST"])
def create_address(request):
    Address.objects.create()
    addresses = Address.objects.filter(status='active')
    serializer = AddressSerializer(addresses, many=True)
    return Response(serializer.data)

#4
@api_view(["PUT"])
def update_address(request, address_id):
    if not Address.objects.filter(address_id=address_id).exists():
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
def delete_address(request, address_id):
    if not Address.objects.filter(address_id=address_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)
    address = Address.objects.get(address_id=address_id)
    address.status = 'inactive'
    address.save()
    addresses = Address.objects.filter(status='active')
    serializer = AddressSerializer(addresses, many=True)
    return Response(serializer.data)

#6
@api_view(["POST"])
def add_address_to_fix(request, address_id):
    if not Address.objects.filter(address_id=address_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)
    address = Address.objects.get(address_id=address_id)
    draft_booking = GetDraftFix()
    if draft_booking is None:
        draft_booking = Fixation.objects.create()
        draft_booking.owner = GetUser()
        draft_booking.created_at = timezone.now()
        draft_booking.save()
    if AddressFixation.objects.filter(fixation=draft_booking, address=address).exists():
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
    item = AddressFixation.objects.create()
    item.fixation = draft_booking
    item.address = address
    item.save()
    serializer = FixationsSerializer(draft_booking, many=False)
    return Response(serializer.data["addresses"])

#7
@api_view(["POST"])
def update_address_image(request, address_id):
    if not Address.objects.filter(address_id=address_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)
    address = Address.objects.get(address_id=address_id)
    image = request.data.get("image")
    if image is not None:
        address.photo = image
        address.save()
    serializer = AddressSerializer(address)
    return Response(serializer.data)

#8
@api_view(["GET"])
def fixations_list(request):
    date_formation_start = request.GET.get("date_formation_start")
    date_formation_end = request.GET.get("date_formation_end")

    fixations = Fixation.objects.all()

    if date_formation_start and parse_datetime(date_formation_start):
        fixations = fixations.filter(created_at__gte=parse_datetime(date_formation_start))

    if date_formation_end and parse_datetime(date_formation_end):
        fixations = fixations.filter(created_at__lt=parse_datetime(date_formation_end))

    serializer = FixationsSerializer(fixations, many=True)
    
    return Response(serializer.data)

#9
@api_view(["GET"])  
def get_fix_by_id(request, fix_id):
    if not Fixation.objects.filter(fixation_id=fix_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)
    fixation = Fixation.objects.get(fixation_id=fix_id)
    serializer = FixationsSerializer(fixation, many=False)
    return Response(serializer.data)

#10
@api_view(["PUT"])
def update_fix_by_id(request, fix_id):
    if not Fixation.objects.filter(fixation_id=fix_id).exists():
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
@api_view(["PUT"])
def update_status_user(request, fix_id):
    if not Fixation.objects.filter(fixation_id=fix_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)
    fixation = Fixation.objects.get(fixation_id=fix_id)
    if fixation.status == 1:
        fixation.status = 2
        fixation.submitted_at = timezone.now()
        fixation.save()
        serializer = FixationsSerializer(fixation, many=False)
        return Response(serializer.data)
    else:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
    
#12
@api_view(["PUT"])
def update_status_admin(request, fix_id):
    if not Fixation.objects.filter(fixation_id=fix_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)
    stat = request.data["status"]
    if stat not in [3, 4]:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
    fixation = Fixation.objects.get(fixation_id=fix_id)
    if fixation.status == 2:
        fixation.completed_at = timezone.now()
        fixation.status = 3
        fixation.moderator = get_moderator()
        fixation.save()
        serializer = FixationsSerializer(fixation, many=False)
        return Response(serializer.data)
    else: 
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
#13
@api_view(["DELETE"])
def delete_fix(request, fix_id):
    if not Fixation.objects.filter(fixation_id=fix_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)
    fixation = Fixation.objects.get(fixation_id=fix_id)
    # if fixation.status != 1:
    #     return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
    fixation.status = 5
    fixation.submitted_at = timezone.now()
    fixation.save()
    serializer = FixationsSerializer(fixation, many=False)
    return Response(serializer.data)
#14
@api_view(["PUT"])
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
def delete_address_from_fix(request, fix_id, address_id):
    if not AddressFixation.objects.filter(fixation_id=fix_id, address_id=address_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)
    item = AddressFixation.objects.get(fixation_id=fix_id, address_id=address_id)
    item.delete()
    fixation = Fixation.objects.get(fixation_id=fix_id)
    serializer = FixationsSerializer(fixation, many=False)
    addresses = serializer.data["addresses"]
    if not len(addresses):
        fixation.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    return Response(addresses)
#16
@api_view(["PUT"])
def update_user(request, user_id):
    if not User.objects.filter(pk=user_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    user = User.objects.get(pk=user_id)
    serializer = UserSerializer(user, data=request.data, many=False, partial=True)

    if not serializer.is_valid():
        return Response(status=status.HTTP_409_CONFLICT)

    serializer.save()

    return Response(serializer.data)
#17
@api_view(["POST"])
def register(request):
    serializer = UserRegisterSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_409_CONFLICT)

    user = serializer.save()

    serializer = UserSerializer(user)

    return Response(serializer.data, status=status.HTTP_201_CREATED)

