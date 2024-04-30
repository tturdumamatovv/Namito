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
            'fields': (
                'title',
                'title_en',
                'title_ru',
                'description',
                'description_en',
                'description_ru',

            )
        }),
        ("Банера", {
            'fields': (
                ('banner1',),
                ('banner2',),
                ('banner3',)
            )
        }),
        ("Сетчики", {
            'fields': (('counter1_title', 'counter1_title_ru', 'counter1_title_en', 'counter1_value'),
                       ('counter2_title', 'counter2_title_ru', 'counter2_title_en', 'counter2_value'),
                       ('counter3_title', 'counter3_title_ru', 'counter3_title_en', 'counter3_value'),)
        }),
        ("Кнопка", {
            'fields': ('button', 'button_ru', 'button_en', 'button_link',)
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
            'fields': ('title', 'title_ru', 'title_en', 'content', 'content_ru', 'content_en', 'image')
        }),
        ('Advanced options', {
            'classes': ('collapse',),
            'fields': ('slug', 'meta_title', 'meta_description', 'meta_image'),
        }),
    )
