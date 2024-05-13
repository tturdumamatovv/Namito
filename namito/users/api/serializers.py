from rest_framework import serializers

from django.conf import settings

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
    profile_picture = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'phone_number', 'profile_picture', 'full_name', 'date_of_birth', 'email', 'first_visit')

    def get_profile_picture(self, obj):
        if obj.profile_picture:
            return obj.profile_picture.url
        else:
            return settings.DEFAULT_AVATAR_URL


class UserAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAddress
        fields = ['id', 'user', 'city', 'street', 'apartment_number', 'entrance',
                  'floor', 'intercom', 'created_at', 'is_primary']  # Include 'is_primary'
        read_only_fields = ['user', 'created_at']


class UserAddressDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAddress
        fields = [field.name for field in UserAddress._meta.fields if field.name not in ('id', 'user')]


class UserAddressUpdateSerializer(serializers.ModelSerializer):
    city = serializers.CharField(required=False)
    is_primary = serializers.BooleanField(required=False)  # Include 'is_primary' as an optional field

    class Meta:
        model = UserAddress
        fields = ['id', 'user', 'city', 'street', 'apartment_number', 'entrance',
                  'floor', 'intercom', 'created_at', 'is_primary']  # Include 'is_primary'
        read_only_fields = ['user', 'created_at']
