from django.urls import path

from namito.advertisement.api.views import AdvertisementView
from namito.pages.api.views import StaticPageDetailView, MainPageView

urlpatterns = [
    path('static-pages/<slug:slug>/', StaticPageDetailView.as_view(), name='static-page-detail'),
    path('static-pages/about-us/', StaticPageDetailView.as_view(), name='about-us-page'),

    path('main-page/', MainPageView.as_view(), name='main-page'),
    path('advertisement/', AdvertisementView.as_view(), name='advertisement'),
]
