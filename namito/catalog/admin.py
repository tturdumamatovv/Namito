from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from mptt.admin import DraggableMPTTAdmin

from .forms import CategoryAdminForm, ColorAdminForm, SizeChartForm, TagAdminForm, ProductForm
from .models import Category, Product, Color, Size, Variant, Image, Review, Brand, SizeChart, SizeChartItem, Tag, \
    StaticPage


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


class VariantInline(admin.TabularInline):
    model = Variant
    extra = 0
    show_change_link = True


class ImageInline(admin.TabularInline):
    model = Image
    extra = 0


class ReviewInline(admin.TabularInline):
    model = Review
    extra = 0
    show_change_link = False
    readonly_fields = ['user', 'text']
    can_delete = False


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    form = ProductForm
    list_display = ['name', 'category']
    search_fields = ['name', 'category__name']
    inlines = [VariantInline, ReviewInline]


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
