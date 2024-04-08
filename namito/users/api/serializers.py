from rest_framework import serializers

from namito.users.models import User


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
        fields = ('id', 'phone_number', 'profile_picture', 'full_name', 'date_of_birth', 'email')
