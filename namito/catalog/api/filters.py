import django_filters
from django.db.models import Avg, Q
from namito.catalog.models import Product, Category



class ProductFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name="name", lookup_expr='icontains')
    min_price = django_filters.NumberFilter(field_name="variants__price", lookup_expr='gte')
    max_price = django_filters.NumberFilter(field_name="variants__price", lookup_expr='lte')
    color = django_filters.CharFilter(field_name="variants__color__name", lookup_expr='iexact')
    size = django_filters.CharFilter(field_name="variants__size__name", lookup_expr='iexact')
    brand = django_filters.CharFilter(field_name="brand__name", lookup_expr='iexact')
    category = django_filters.ModelChoiceFilter(
        field_name='category',
        queryset=Category.objects.all(),
        method='filter_by_category'
    )
    min_rating = django_filters.NumberFilter(method='filter_by_min_rating')
    has_discount = django_filters.BooleanFilter(method='filter_by_discount_presence')

    class Meta:
        model = Product
        fields = ['name', 'min_price', 'max_price', 'color', 'size', 'brand', 'category', 'min_rating', 'has_discount']

    def filter_by_min_rating(self, queryset, name, value):
        queryset = queryset.annotate(avg_rating=Avg('ratings__score')).filter(avg_rating__gte=value)
        return queryset.distinct()

    def filter_by_discount_presence(self, queryset, name, value):
        if value:
            return queryset.filter(
                Q(variants__discount_value__gt=0) &
                Q(variants__discount_type__isnull=False)
            ).distinct()
        else:
            return queryset.exclude(
                Q(variants__discount_value__gt=0) &
                Q(variants__discount_type__isnull=False)
            ).distinct()

    def sort_by_discount(self, queryset, order):
        if order == 'asc':
            return queryset.order_by('variants__discount_value').distinct()
        elif order == 'desc':
            return queryset.order_by('-variants__discount_value').distinct()
        else:
            return queryset

    @property
    def qs(self):
        queryset = super().qs

        queryset = self.apply_filters(queryset)

        sort_by_discount = self.request.GET.get('sort_by_discount')
        if sort_by_discount:
            queryset = self.sort_by_discount(queryset, sort_by_discount)

        return queryset.distinct()

    def filter_by_category(self, queryset, name, value):
        category = value
        descendants = category.get_descendants(include_self=True)
        descendant_ids = descendants.values_list('id', flat=True)
        return queryset.filter(category__id__in=descendant_ids)

    def apply_filters(self, queryset):
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
            if 'category' in self.request.GET:
                queryset = queryset.filter(category__name__iexact=self.request.GET['category'])
            if 'min_rating' in self.request.GET:
                queryset = self.filter_by_min_rating(queryset, 'min_rating', float(self.request.GET['min_rating']))
            if 'has_discount' in self.request.GET:
                has_discount = self.request.GET['has_discount'].lower() == 'true'
                queryset = self.filter_by_discount_presence(queryset, 'has_discount', has_discount)

        return queryset
