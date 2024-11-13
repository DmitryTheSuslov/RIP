from rest_framework import serializers
from .models import *
from django.contrib.auth.models import User
from collections import OrderedDict

class FixationsSerializer(serializers.ModelSerializer):
    owner = serializers.SerializerMethodField()
    moderator = serializers.SerializerMethodField()
    addresses = serializers.SerializerMethodField()
    addresses_count = serializers.SerializerMethodField()
    
    def get_owner(self, obj):
        return obj.owner.username
    
    def get_moderator(self, application):
        if application.moderator:
            return application.moderator.username

    def get_addresses(self, fix):
        addresses = Address.objects.all()
        # addresses = AddressFixation.objects.filter(fixation=fix)
        return AddressInfoSerializer(addresses, many=True).data

    def get_addresses_count(self, obj):
        return AddressFixation.objects.filter(fixation=obj).count()
    
    class Meta:
        model = Fixation
        fields = ['fixation_id', 'status', 'month', 'addresses', 'created_at', 'submitted_at', 'completed_at', 'owner', 'moderator', 'addresses_count']
    
class AddressFixationSerializer(serializers.ModelSerializer):
    class Meta:
        model = AddressFixation
        fields = "__all__"

class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = "__all__"

    def get_fields(self):
        new_fields = OrderedDict()
        for name, field in super().get_fields().items():
            field.required = False
            new_fields[name] = field
        return new_fields

class AddressInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = "__all__"


class UserRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'password', 'first_name', 'last_name', 'username')
        write_only_fields = ('password',)
        read_only_fields = ('id',)  

    def create(self, validated_data):
        user = User.objects.create(
                email=validated_data['email'],
                first_name=validated_data['first_name'],
                last_name=validated_data['last_name'],
                username=validated_data['username']
            )
        user.set_password(validated_data['password'])
        user.save()
        return user

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'password', 'first_name', 'last_name', 'date_joined', 'password', 'username']

class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True)