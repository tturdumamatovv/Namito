from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from firebase_admin import auth as firebase_auth
import firebase_admin
from firebase_admin import credentials

from namito.users.models import (
    User,
    UserAddress
)
from .serializers import (
    CustomUserSerializer,
    VerifyCodeSerializer,
    UserProfileSerializer,
    UserAddressSerializer,
    UserAddressUpdateSerializer
)
from namito.users.utils import (
    send_sms,
    generate_confirmation_code,
)


cred = credentials.Certificate("firebase_key.json")
firebase_admin.initialize_app(cred)


class UserLoginView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer

    def create(self, request, *args, **kwargs):
        phone_number = request.data.get('phone_number')
        if not phone_number:
            return Response({'error': 'Phone number is required.'}, status=status.HTTP_400_BAD_REQUEST)
        if not phone_number.startswith("+996"):
            return Response({'error': 'Phone number must start with "+996".'}, status=status.HTTP_400_BAD_REQUEST)
        elif len(phone_number) != 13:
            return Response({'error': 'Phone number must be 13 digits long including the country code.'}, status=status.HTTP_400_BAD_REQUEST)
        elif not phone_number[4:].isdigit():
            return Response({'error': 'Invalid characters in phone number. Only digits are allowed after the country code.'}, status=status.HTTP_400_BAD_REQUEST)

        confirmation_code = generate_confirmation_code()
        send_sms(phone_number, confirmation_code)

        User.objects.update_or_create(
            phone_number=phone_number,
            defaults={'code': confirmation_code}
        )

        response_data = {
            'message': 'Confirmation code sent successfully.',
            'code': confirmation_code
        }
        return Response(response_data, status=status.HTTP_200_OK)


class VerifyCodeView(generics.CreateAPIView):
    serializer_class = VerifyCodeSerializer

    def create(self, request, *args, **kwargs):
        code = request.data.get('code')

        if not code:
            return Response({'error': 'Code is required.'}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.filter(code=code).first()
        if not user:
            return Response({'error': 'Invalid code.'}, status=status.HTTP_400_BAD_REQUEST)

        user.is_verified = True
        user.code = None
        user.save()

        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)

        return Response({
            'access_token': access_token,
            'refresh_token': str(refresh),
            'first_visit': user.first_visit},
            status=status.HTTP_200_OK)


class UserProfileUpdateView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    # parser_classes = [MultiPartParser, FormParser]

    def get_object(self):
        return self.request.user

    def put(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        if all(serializer.validated_data.get(field) for field in ['full_name', 'date_of_birth', 'email']):
            instance.first_visit = False
            instance.save()

        return Response(serializer.data)

    def get(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class UserAddressCreateAPIView(generics.ListCreateAPIView):
    queryset = UserAddress.objects.all()
    serializer_class = UserAddressSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return UserAddress.objects.filter(user=user)

    def perform_create(self, serializer):
        user = self.request.user

        serializer.save(user=user)


class UserAddressUpdateAPIView(generics.RetrieveUpdateAPIView):
    queryset = UserAddress.objects.all()
    serializer_class = UserAddressUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_update(self, serializer):
        user = self.request.user

        # Check if 'is_primary' is set to True
        if serializer.validated_data.get('is_primary', False):
            # Set 'is_primary' of all other addresses to False for this user
            UserAddress.objects.filter(user=user, is_primary=True).update(is_primary=False)

        # Perform the update
        serializer.save()


class UserAddressDeleteAPIView(generics.RetrieveDestroyAPIView):
    queryset = UserAddress.objects.all()
    serializer_class = UserAddressSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return UserAddress.objects.filter(user=user)


@csrf_exempt
def google_login(request):
    if request.method == 'POST':
        # Получаем токен от фронтенда
        token = request.POST.get('id_token')
        if not token:
            return JsonResponse({'status': 'error', 'message': 'ID token is required.'}, status=400)

        # Верификация токена с помощью Firebase
        try:
            decoded_token = firebase_auth.verify_id_token(token)
            uid = decoded_token['uid']
            email = decoded_token.get('email')

            # Найдите или создайте пользователя в вашей базе данных
            user, created = User.objects.get_or_create(email=email, defaults={'username': uid})

            # Здесь можно создать JWT токен или установить сессию для пользователя

            # Пример: Возврат успешного ответа
            return JsonResponse({'status': 'success', 'user_id': user.id})

        except Exception as e:
            # Обработка ошибок верификации
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    else:
        return JsonResponse({'status': 'error', 'message': 'Only POST requests are allowed'}, status=405)
