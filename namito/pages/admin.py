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
                'title_ru',
                'title_en',
                'description',
                'description_ru',
                'description_en',
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
            'fields': (('counter1_title', 'counter1_title_ru', 'counter1_title_en', 'counter1_value', 'counter1_value_ru', 'counter1_value_en'),
                       ('counter2_title', 'counter2_title_ru', 'counter2_title_en', 'counter2_value', 'counter2_value_ru', 'counter2_value_en'),
                       ('counter3_title', 'counter3_title_ru', 'counter3_title_en', 'counter3_value', 'counter3_value_ru', 'counter3_value_en'),)
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
