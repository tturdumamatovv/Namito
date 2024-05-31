import django_filters
from django.db.models import Avg, Q
from namito.catalog.models import Product, Category


class ProductFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name="name", lookup_expr='icontains')
    min_price = django_filters.NumberFilter(field_name="variants__price", lookup_expr='gte')
    max_price = django_filters.NumberFilter(field_name="variants__price", lookup_expr='lte')
    brand = django_filters.CharFilter(method='filter_by_brands')
    category_slug = django_filters.CharFilter(method='filter_by_category_slug')
    min_rating = django_filters.NumberFilter(method='filter_by_min_rating')
    has_discount = django_filters.BooleanFilter(method='filter_by_discount_presence')
    color = django_filters.CharFilter(method='filter_by_colors')
    size = django_filters.CharFilter(method='filter_by_sizes')

    class Meta:
        model = Product
        fields = ['name', 'min_price', 'max_price', 'brand', 'category_slug',
                  'min_rating', 'has_discount', 'color', 'size']

    def filter_by_category_slug(self, queryset, name, value):
        category = Category.objects.filter(slug=value).first()
        if category:
            descendant_categories = category.get_descendants(include_self=True)
            return queryset.filter(category__in=descendant_categories)
        return queryset.none()

    def filter_by_brands(self, queryset, name, value):
        brands = value.split(',')
        return queryset.filter(brand__name__in=brands)

    def filter_by_colors(self, queryset, name, value):
        colors = value.split(',')
        return queryset.filter(variants__color__id__in=colors)

    def filter_by_sizes(self, queryset, name, value):
        sizes = value.split(',')
        return queryset.filter(variants__size__name__in=sizes)

    def filter_by_min_rating(self, queryset, name, value):
        queryset = queryset.annotate(
            avg_rating=Avg('reviews__rating')  # Обратите внимание на путь к рейтингу
        ).filter(
            Q(avg_rating__gte=value) | Q(avg_rating__isnull=False)
        )
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

        # Применяем фильтры из запроса
        queryset = self.apply_filters(queryset)

        # Обрабатываем сортировку по скидке, если требуется
        sort_by_discount = self.request.GET.get('sort_by_discount')
        if sort_by_discount:
            queryset = self.sort_by_discount(queryset, sort_by_discount)

        return queryset.distinct()

    def apply_filters(self, queryset):
        if self.request:
            if 'min_price' in self.request.GET:
                queryset = queryset.filter(variants__price__gte=self.request.GET['min_price'])
            if 'max_price' in self.request.GET:
                queryset = queryset.filter(variants__price__lte=self.request.GET['max_price'])
            if 'color_id' in self.request.GET:
                queryset = self.filter_by_colors(queryset, 'color_id', self.request.GET.getlist('color_id'))
            if 'size' in self.request.GET:
                queryset = self.filter_by_sizes(queryset, 'size', self.request.GET.get('size'))
            if 'brand' in self.request.GET:
                queryset = self.filter_by_brands(queryset, 'brand', self.request.GET.get('brand'))
            if 'category_slug' in self.request.GET:  # измененная часть
                queryset = self.filter_by_category_slug(queryset, 'category_slug',
                                                        self.request.GET.get('category_slug'))
            if 'min_rating' in self.request.GET:
                queryset = self.filter_by_min_rating(queryset, 'min_rating', float(self.request.GET['min_rating']))
            if 'has_discount' in self.request.GET:
                has_discount = self.request.GET['has_discount'].lower() == 'true'
                queryset = self.filter_by_discount_presence(queryset, 'has_discount', has_discount)

        return queryset
