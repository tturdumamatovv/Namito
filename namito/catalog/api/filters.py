import django_filters
from django.db.models import Avg

from namito.catalog.models import Product



class ProductFilter(django_filters.FilterSet):
    min_price = django_filters.NumberFilter(field_name="variants__price", lookup_expr='gte')
    max_price = django_filters.NumberFilter(field_name="variants__price", lookup_expr='lte')
    color = django_filters.CharFilter(field_name="variants__color__name", lookup_expr='iexact')
    size = django_filters.CharFilter(field_name="variants__size__name", lookup_expr='iexact')
    brand = django_filters.CharFilter(field_name="brand__name", lookup_expr='iexact')
    min_rating = django_filters.NumberFilter(method='filter_by_min_rating')

    class Meta:
        model = Product
        fields = ['min_price', 'max_price', 'color', 'size', 'brand', 'min_rating']

    def filter_by_min_rating(self, queryset, name, value):
        return queryset.annotate(avg_rating=Avg('ratings__score')).filter(avg_rating__gte=value)
