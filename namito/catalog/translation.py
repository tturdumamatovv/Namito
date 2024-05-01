from modeltranslation.translator import (
    register,
    TranslationOptions
)

from .models import (
    Category,
    Brand,
    Tag,
    Product,
    Review,
    Characteristic,
    Color,
    Size
)


@register(Category)
class CategoryTranslationOptions(TranslationOptions):
    fields = ('name', 'type',)


@register(Brand)
class BrandTranslationOptions(TranslationOptions):
    fields = ('name',)


@register(Tag)
class TagTranslationOptions(TranslationOptions):
    fields = ('name',)


@register(Product)
class ProductTranslationOptions(TranslationOptions):
    fields = ('name', 'description',)


@register(Color)
class ColorTranslationOptions(TranslationOptions):
    fields = ('name',)


@register(Size)
class SizeTranslationOptions(TranslationOptions):
    fields = ('name',)


@register(Review)
class ReviewTranslationOptions(TranslationOptions):
    fields = ('text',)


@register(Characteristic)
class CharacteristicTranslationOptions(TranslationOptions):
    fields = ('key', 'value')
