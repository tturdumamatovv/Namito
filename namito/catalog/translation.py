from modeltranslation.translator import (
    register,
    TranslationOptions
)

from namito.catalog.models import (
    Category,
    Tag,
    Product,
    Characteristic,
    Color,
)


@register(Category)
class CategoryTranslationOptions(TranslationOptions):
    fields = ('name', 'type',)


@register(Tag)
class TagTranslationOptions(TranslationOptions):
    fields = ('name',)


@register(Product)
class ProductTranslationOptions(TranslationOptions):
    fields = ('name', 'description',)


@register(Color)
class ColorTranslationOptions(TranslationOptions):
    fields = ('name',)


@register(Characteristic)
class CharacteristicTranslationOptions(TranslationOptions):
    fields = ('key', 'value')
