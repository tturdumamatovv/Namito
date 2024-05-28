from modeltranslation.translator import register, TranslationOptions
from .models import MainPage, MainPageSlider, StaticPage, FAQ


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


@register(FAQ)
class FAQTranslationOptions(TranslationOptions):
    fields = ('question', 'answer')
