from django.urls import path

from namito.advertisement.api.views import NotificationList


urlpatterns = [
    path('notification/', NotificationList.as_view(), name='notification')

]
