from django.contrib import admin

# Register your models here.
from namito.advertisement.admin import AdvertisementInline
from namito.pages.models import StaticPage, MainPageSlider, MainPage


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
