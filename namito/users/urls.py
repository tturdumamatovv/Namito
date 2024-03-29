from django.urls import path


from namito.users.api.views import UserLoginView, VerifyCodeView, UserProfileUpdateView

urlpatterns = [
    path('login/', UserLoginView.as_view(), name='user_registration'),
    path('verify-code/', VerifyCodeView.as_view(), name='verify_code'),
    path('profile/', UserProfileUpdateView.as_view(), name='user-profile'),
]
