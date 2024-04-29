from modeltranslation.translator import register, TranslationOptions
from .models import MainPage, MainPageSlider, StaticPage


@register(MainPage)
class MainPageTranslationOptions(TranslationOptions):
    fields = (
        'title', 'description', 'counter1_title', 'counter1_value', 'counter2_title', 'counter2_value',
        'counter3_title',
        'counter3_value', 'button')


@register(MainPageSlider)
class MainPageSliderTranslationOptions(TranslationOptions):
    fields = ('title', 'description')


@register(StaticPage)
class StaticPageTranslationOptions(TranslationOptions):
    fields = ('title', 'content', 'meta_title', 'meta_description')
