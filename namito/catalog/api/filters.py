import django_filters
from django.db.models import Avg

from namito.catalog.models import Product



class ProductFilter(django_filters.FilterSet):
    min_price = django_filters.NumberFilter(field_name="variants__price", lookup_expr='gte')
    max_price = django_filters.NumberFilter(field_name="variants__price", lookup_expr='lte')
    color = django_filters.CharFilter(field_name="variants__color__name", lookup_expr='iexact')
    size = django_filters.CharFilter(field_name="variants__size__name", lookup_expr='iexact')
    brand = django_filters.CharFilter(field_name="brand__name", lookup_expr='iexact')
    category = django_filters.CharFilter(field_name="category__name", lookup_expr='iexact')
    min_rating = django_filters.NumberFilter(method='filter_by_min_rating')

    class Meta:
        model = Product
        fields = ['min_price', 'max_price', 'color', 'size', 'brand', 'min_rating']

    def filter_by_min_rating(self, queryset, name, value):
        queryset = queryset.annotate(avg_rating=Avg('ratings__score')).filter(avg_rating__gte=value)
        return queryset.distinct()

    @property
    def qs(self):
        queryset = super().qs
        if self.request:
            if 'min_price' in self.request.GET:
                queryset = queryset.filter(variants__price__gte=self.request.GET['min_price'])
            if 'max_price' in self.request.GET:
                queryset = queryset.filter(variants__price__lte=self.request.GET['max_price'])
            if 'color' in self.request.GET:
                queryset = queryset.filter(variants__color__name__iexact=self.request.GET['color'])
            if 'size' in self.request.GET:
                queryset = queryset.filter(variants__size__name__iexact=self.request.GET['size'])
            if 'brand' in self.request.GET:
                queryset = queryset.filter(brand__name__iexact=self.request.GET['brand'])
        return queryset.distinct()

