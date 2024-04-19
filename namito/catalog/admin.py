from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from mptt.admin import DraggableMPTTAdmin
import nested_admin

from .forms import (
    CategoryAdminForm,
    ColorAdminForm,
    SizeChartForm,
    TagAdminForm,
    ProductForm
)
from .models import (
    Category,
    Product,
    Color,
    Size,
    Variant,
    Image,
    Review,
    Brand,
    SizeChart,
    SizeChartItem,
    Tag,
    StaticPage,
    MainPage,
    Advertisement,
    MainPageSlider,
    Characteristics
)


@admin.register(StaticPage)
class StaticPageAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'created_at', 'updated_at')
    search_fields = ['title', 'content']
    prepopulated_fields = {'slug': ('title',)}
    list_filter = ('created_at', 'updated_at')
    ordering = ('title',)
    fieldsets = (
        (None, {
            'fields': ('title', 'content', 'meta_title', 'meta_description', 'image')
        }),
        ('Advanced options', {
            'classes': ('collapse',),
            'fields': ('slug',),
        }),
    )


@admin.register(Category)
class CategoryAdmin(DraggableMPTTAdmin):
    form = CategoryAdminForm

    list_display = [
        "tree_actions",
        "indented_name",
        "id",
        "name",
        "order",
        "parent",
    ]

    list_display_links = ("indented_name",)
    list_filter = [
        "parent",
    ]
    search_fields = ["id", "name"]
    list_select_related = ["parent"]
    mptt_level_indent = 20

    @admin.display(description="Name")
    def indented_name(self, instance):
        return f'{instance.name}'


class ImageInline(nested_admin.NestedTabularInline):
    model = Image
    extra = 0
    readonly_fields = ("get_image",)

    def get_image(self, obj):
        return mark_safe(f'<img src = {obj.image.url} width = "300"')

    get_image.short_description = "Изображение"


class VariantInline(nested_admin.NestedTabularInline):
    model = Variant
    extra = 0
    show_change_link = True
    inlines = [ImageInline]


class ReviewInline(nested_admin.NestedTabularInline):
    model = Review
    extra = 0
    show_change_link = False
    readonly_fields = ['user', 'text']
    can_delete = False


class CharacteristicsInline(nested_admin.NestedTabularInline):
    model = Characteristics
    extra = 0
    show_change_link = True
    readonly_fields = ['key', 'value']


@admin.register(Product)
class ProductAdmin(nested_admin.NestedModelAdmin):
    form = ProductForm
    list_display = ['name', 'category']
    search_fields = ['name', 'category__name']
    inlines = [CharacteristicsInline, VariantInline, ReviewInline]

    class Media:
        css = {
            "all": ("css/admin.css",)
        }


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('name', 'logo_preview')
    search_fields = ('name',)
    readonly_fields = ('logo_preview',)

    def logo_preview(self, obj):
        if obj.logo:
            return mark_safe('<img src="{}" width="150" height="auto" />'.format(obj.logo.url))
        return "No Image"

    logo_preview.short_description = 'Logo Preview'


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'color']
    search_fields = ['name']
    form = TagAdminForm


@admin.register(Color)
class ColorAdmin(admin.ModelAdmin):
    list_display = ['name', 'color']
    search_fields = ['name']
    form = ColorAdminForm


@admin.register(Size)
class SizeAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']
    search_fields = ['name']


@admin.register(Variant)
class VariantAdmin(admin.ModelAdmin):
    list_display = ['product', 'color', 'size', 'price']
    search_fields = ['product__name', 'color__name', 'size__name']
    inlines = [ImageInline]


@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = ['variant', 'image_preview']

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="100" style="border-radius: 5px;"/>', obj.image.url)
        return "No Image"

    image_preview.short_description = 'Preview'


class SizeChartItemInline(admin.TabularInline):
    model = SizeChartItem
    extra = 0


@admin.register(SizeChart)
class SizeChartAdmin(admin.ModelAdmin):
    form = SizeChartForm
    list_display = ('name',)
    inlines = [SizeChartItemInline]


class AdvertisementInline(admin.TabularInline):
    model = Advertisement
    extra = 0


class MainPageSliderInline(admin.TabularInline):
    model = MainPageSlider
    extra = 0


@admin.register(MainPage)
class MainPageAdmin(admin.ModelAdmin):
    list_display = ('title', 'description', 'button', 'button_link',)
    inlines = [AdvertisementInline, MainPageSliderInline]
    fieldsets = (
        (None, {
            'fields': ('title', 'description',)
        }),
        ("Банера", {
            'fields': (
                ('banner1', 'banner1_link'),
                ('banner2', 'banner2_link'),
                ('banner3', 'banner3_link')
            )
        }),
        ("Сетчики", {
            'fields': (('counter1_title', 'counter1_value'),
                       ('counter2_title', 'counter2_value'),
                       ('counter3_title', 'counter3_value'),)
        }),
        ("Кнопка", {
            'fields': ('button', 'button_link',)
        }),
    )
