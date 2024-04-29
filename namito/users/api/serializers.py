from rest_framework import serializers

from namito.users.models import User
from namito.users.models import UserAddress


class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'phone_number', 'full_name', 'date_of_birth', 'email')
        read_only_fields = ('full_name', 'date_of_birth', 'email')


class VerifyCodeSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=4)


class UserProfileSerializer(serializers.ModelSerializer):
    phone_number = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = ('id', 'phone_number', 'profile_picture', 'full_name', 'date_of_birth', 'email', 'first_visit')


class UserAddressSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserAddress
        fields = ['id', 'user', 'city', 'apartment_number', 'entrance', 'floor', 'intercom', 'created_at']
        read_only_fields = ['user', 'created_at']


class UserAddressDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAddress
        fields = [field.name for field in UserAddress._meta.fields if field.name not in ('id', 'user')]


class UserAddressUpdateSerializer(serializers.ModelSerializer):
    city = serializers.CharField(required=False)

    class Meta:
        model = UserAddress
        fields = ['id', 'user', 'city', 'apartment_number', 'entrance', 'floor', 'intercom', 'created_at']
        read_only_fields = ['user', 'created_at']
