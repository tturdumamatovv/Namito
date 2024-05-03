from modeltranslation.translator import (
    register,
    TranslationOptions
)

from .models import Advertisement


@register(Advertisement)
class AdvertisementTranslationOptions(TranslationOptions):
    fields = ('title', 'description', 'button')
