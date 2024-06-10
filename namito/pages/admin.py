from django.contrib import admin

# Register your models here.
from namito.advertisement.admin import AdvertisementInline
from namito.pages.models import (StaticPage, MainPageSlider, MainPage, Phone, Email, SocialLink,
                                 Contacts, Address, PaymentMethod, FAQ, MainPageLayoutMeta)


class MainPageSliderInline(admin.StackedInline):
    model = MainPageSlider
    extra = 0


class MainPageLayoutInline(admin.StackedInline):
    model = MainPageLayoutMeta
    extra = 0


@admin.register(MainPage)
class MainPageAdmin(admin.ModelAdmin):
    list_display = ('title', 'description', 'button', 'button_link',)
    inlines = [AdvertisementInline, MainPageSliderInline, MainPageLayoutInline]
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


class FAQInline(admin.StackedInline):
    model = FAQ
    extra = 1


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
        ('Расширенные параметры', {
            'fields': ('slug', 'meta_title', 'meta_description', 'meta_image'),
        }),
    )
    inlines = [FAQInline]


class PhoneInline(admin.TabularInline):
    model = Phone
    extra = 1


class EmailInline(admin.TabularInline):
    model = Email
    extra = 1


class SocialLinkInline(admin.TabularInline):
    model = SocialLink
    extra = 1


class PaymentMethodLinkInline(admin.TabularInline):
    model = PaymentMethod
    extra = 1


class AddressInline(admin.TabularInline):
    model = Address
    extra = 1


@admin.register(Contacts)
class ContactsAdmin(admin.ModelAdmin):
    inlines = [PhoneInline, EmailInline, SocialLinkInline, PaymentMethodLinkInline, AddressInline]
