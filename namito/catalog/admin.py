import nested_admin

from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from mptt.admin import DraggableMPTTAdmin

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
    Characteristic,
    ReviewImage
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
        return mark_safe(f'<img src = {obj.media.url} width = "300"')

    get_image.short_description = "Изображение"


class VariantInline(nested_admin.NestedTabularInline):
    model = Variant
    extra = 0
    show_change_link = True


class ReviewImageInline(nested_admin.NestedTabularInline):
    model = ReviewImage
    extra = 0
    readonly_fields = ("get_image",)

    def get_image(self, obj):
        return mark_safe(f'<img src="{obj.image.url}" width="150" height="auto" />')

    get_image.short_description = "Image Preview"


class ReviewInline(nested_admin.NestedTabularInline):
    model = Review
    extra = 0
    show_change_link = False
    fields = ['user', 'text', 'rating']
    can_delete = False
    inlines = [ReviewImageInline]


class CharacteristicsInline(nested_admin.NestedTabularInline):
    model = Characteristic
    extra = 0
    show_change_link = True
    fields = ['key_ru', 'key_en', 'value_ru', 'value_en']


class ImageInlineWithColor(nested_admin.NestedTabularInline):
    model = Image
    extra = 0
    fields = ['image', 'color']  # Добавляем поле 'color' в список полей для отображения и редактирования
    readonly_fields = ("get_image",)

    def get_image(self, obj):
        return mark_safe(f'<img src="{obj.image.url}" width="300" />')

    get_image.short_description = "Image Preview"


@admin.register(Product)
class ProductAdmin(nested_admin.NestedModelAdmin):
    form = ProductForm
    list_display = ['name_ru', 'name_en', 'category', 'active']
    search_fields = ['name', 'category__name']
    inlines = [CharacteristicsInline, VariantInline, ReviewInline, ImageInlineWithColor]

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
    list_display = ['name_en', 'name_ru', 'color']
    search_fields = ['name_en', 'name_ru',]
    form = TagAdminForm


@admin.register(Color)
class ColorAdmin(admin.ModelAdmin):
    list_display = ['name_en', 'name_ru', 'color']
    search_fields = ['name_en', 'name_ru',]
    form = ColorAdminForm


@admin.register(Size)
class SizeAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']
    search_fields = ['name']


@admin.register(Variant)
class VariantAdmin(admin.ModelAdmin):
    list_display = ['product', 'color', 'size', 'price']
    search_fields = ['product__name', 'color__name', 'size__name']


@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = ['image_preview', 'color']
    readonly_fields = ['small_image']
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
