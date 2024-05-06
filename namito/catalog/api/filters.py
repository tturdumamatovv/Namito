import django_filters
from django.db.models import Avg, Q
from namito.catalog.models import Product, Size, Color


class ProductFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name="name", lookup_expr='icontains')
    min_price = django_filters.NumberFilter(field_name="variants__price", lookup_expr='gte')
    max_price = django_filters.NumberFilter(field_name="variants__price", lookup_expr='lte')

    # Используем MultipleChoiceFilter для фильтрации по цвету
    color = django_filters.MultipleChoiceFilter(
        field_name='variants__color__name',
        choices=lambda: [(color.name, color.name) for color in Color.objects.all()],
        lookup_expr='in'
    )

    # Используем MultipleChoiceFilter для фильтрации по размеру
    size = django_filters.MultipleChoiceFilter(
        field_name='variants__size__name',
        choices=lambda: [(size.name, size.name) for size in Size.objects.all()],
        lookup_expr='in'
    )

    brand = django_filters.MultipleChoiceFilter(
        field_name="brand__name",
        choices=lambda: [(brand, brand) for brand in Product.objects.values_list('brand__name', flat=True).distinct()],
        lookup_expr='in'
    )

    category = django_filters.CharFilter(field_name="category__name", lookup_expr='iexact')
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

        sort_by_discount = self.request.GET.get('sort_by_discount')
        if sort_by_discount:
            queryset = self.sort_by_discount(queryset, sort_by_discount)

        # Применение остальных фильтров
        queryset = self.apply_filters(queryset)
        return queryset.distinct()

    def apply_filters(self, queryset):
        if self.request:
            if 'min_price' in self.request.GET:
                queryset = queryset.filter(variants__price__gte=self.request.GET['min_price'])
            if 'max_price' in self.request.GET:
                queryset = queryset.filter(variants__price__lte=self.request.GET['max_price'])
            if 'color' in self.request.GET:
                colors = self.request.GET.getlist('color')
                queryset = queryset.filter(variants__color__name__in=colors)
            if 'size' in self.request.GET:
                sizes = self.request.GET.getlist('size')
                queryset = queryset.filter(variants__size__name__in=sizes)
            if 'brand' in self.request.GET:
                brands = self.request.GET.getlist('brand')
                queryset = queryset.filter(brand__name__in=brands)
            if 'category' in self.request.GET:
                queryset = queryset.filter(category__name__iexact=self.request.GET['category'])
            if 'min_rating' in self.request.GET:
                queryset = self.filter_by_min_rating(queryset, 'min_rating', float(self.request.GET['min_rating']))
            if 'has_discount' in self.request.GET:
                has_discount = self.request.GET['has_discount'].lower() == 'true'
                queryset = self.filter_by_discount_presence(queryset, 'has_discount', has_discount)

        return queryset
