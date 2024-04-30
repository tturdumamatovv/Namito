from modeltranslation.translator import register, TranslationOptions
from .models import MainPage, MainPageSlider, StaticPage


@register(MainPage)
class MainPageTranslationOptions(TranslationOptions):
    fields = (
        'title', 'description', 'counter1_title', 'counter2_title',
        'counter3_title', 'button')


@register(MainPageSlider)
class MainPageSliderTranslationOptions(TranslationOptions):
    fields = ('title', 'description')


@register(StaticPage)
class StaticPageTranslationOptions(TranslationOptions):
    fields = ('title', 'content', 'meta_title', 'meta_description')
