from django.urls import path


from namito.users.api.views import (
    UserLoginView,
    VerifyCodeView,
    UserProfileUpdateView,
    UserAddressCreateAPIView,
    UserAddressUpdateAPIView,
    UserAddressDeleteAPIView,
    )

urlpatterns = [
    path('login/', UserLoginView.as_view(), name='user_registration'),
    path('verify-code/', VerifyCodeView.as_view(), name='verify_code'),
    path('profile/', UserProfileUpdateView.as_view(), name='user-profile'),
    path('addresses/create/', UserAddressCreateAPIView.as_view(), name='create_address'),
    path('addresses/<int:pk>/update/', UserAddressUpdateAPIView.as_view(), name='update_address'),
    path('addresses/<int:pk>/delete/', UserAddressDeleteAPIView.as_view(), name='delete_address'),
]
