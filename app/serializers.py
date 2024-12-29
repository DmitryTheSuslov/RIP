from rest_framework import serializers
from .models import *
from django.contrib.auth.models import User
from collections import OrderedDict

class FixationsSerializer(serializers.ModelSerializer):
    owner = serializers.SerializerMethodField()
    moderator = serializers.SerializerMethodField()
    addresses = serializers.SerializerMethodField()
    addresses_count = serializers.SerializerMethodField()
    pay_date = serializers.SerializerMethodField()
    
    def get_owner(self, obj):
        return obj.owner.username
    
    def get_moderator(self, application):
        if application.moderator:
            return application.moderator.username

    def get_addresses(self, fix):
        # addresses = Address.objects.all()
        addresses = [x.address for x in AddressFixation.objects.filter(fixation=fix)]
        data = AddressSerializer(addresses, many=True).data
        for i, elem in enumerate(data):
            elem["counter_value"] = addresses[i].get_counter_value(fix)
        return data

    def get_addresses_count(self, obj):
        return AddressFixation.objects.filter(fixation=obj).count()
    
    def get_pay_date(self, obj):
        try:
            return AddressFixation.objects.filter(fixation=obj).all()[0].pay_date
        except:
            return None
    
    class Meta:
        model = Fixation
        fields = ['fixation_id', 'status', 'month', 'addresses', 'created_at', 'submitted_at', 'completed_at', 'owner', 'moderator', 'addresses_count', 'pay_date']
    
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

    def get_counter_value(self, address):
        fix = self.context.get("fixation")
        if fix:
            address_fix = AddressFixation.objects.filter(address=address, fixation=fix).first()
            return address_fix.water_counter_value
        return None

    def get_fields(self):
        new_fields = OrderedDict()
        for name, field in super().get_fields().items():
            field.required = False
            new_fields[name] = field
        return new_fields


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