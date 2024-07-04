import html
import re
import io
import uuid

from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from django.core.files.base import ContentFile
from django.conf import settings
from django.db.models import Avg

from mptt.models import MPTTModel, TreeForeignKey
from colorfield.fields import ColorField
from PIL import Image as PILImage
from unidecode import unidecode

from namito.users.models import User


class ProcessedImageModel(models.Model):
    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.process_image()
        super().save(*args, **kwargs)

    def process_image(self):
        if self.image:
            pil_image = PILImage.open(self.image)
            if pil_image.format != 'WEBP':
                output_io_stream = io.BytesIO()
                pil_image.convert('RGB').save(output_io_stream, format='WEBP', quality=70)
                output_io_stream.seek(0)
                self.image = ContentFile(output_io_stream.read(),
                                         name=self.image.name.split('.')[0] + '.webp')


class Category(MPTTModel, models.Model):
    CATEGORY_TYPES = [
        (0, _("For men")),
        (1, _("For woman")),
        (2, _("For children")),
        (3, _("Unisex"))
    ]
    name = models.CharField(max_length=255, verbose_name=_('Название'))
    type = models.IntegerField(choices=CATEGORY_TYPES, default=3, verbose_name=_('Тип'))
    slug = models.SlugField(max_length=255, unique=True, blank=True, null=True, verbose_name=_('Слаг'))
    image = models.ImageField(null=True, blank=True, verbose_name=_('Изображение'))
    background_color = ColorField(default='#FF0000', null=True, verbose_name=_('Фоновый цвет'))
    parent = TreeForeignKey("self", on_delete=models.SET_NULL, null=True, blank=True,
                            related_name="children", verbose_name=_("Родительская категория"))
    order = models.PositiveIntegerField(default=0, editable=False, db_index=True, verbose_name=_('Порядок'))
    meta_title = models.CharField(max_length=59, blank=True, null=True, verbose_name=_('Мета заголовок'))
    meta_description = models.TextField(blank=True, null=True, verbose_name=_('Мета описание'))
    meta_image = models.ImageField(null=True, blank=True, verbose_name=_('Мета изображение'))
    promotion = models.BooleanField(default=False, verbose_name=_('Продвижение'))
    icon = models.ImageField(upload_to='category_icons/', null=True, blank=True, verbose_name=_('Иконки'))

    class Meta:
        verbose_name = _("Категория")
        verbose_name_plural = _("Категории")
        ordering = ["order", "name"]

    class MPTTMeta:
        order_insertion_by = ["name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(unidecode(self.name))
            unique_slug = base_slug
            counter = 1
            while Category.objects.filter(slug=unique_slug).exists():
                unique_slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = unique_slug
        super().save(*args, **kwargs)

        if not self.meta_title:
            self.meta_title = self.name

        if not self.meta_description:
            self.meta_description = self.name

        # Automatically set meta image if not provided
        if not self.meta_image and self.image:
            self.meta_image = self.image

        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.name}'


class Brand(models.Model):
    name = models.CharField(max_length=255, unique=True, help_text="The name of the brand", verbose_name=_('Название'))
    logo = models.ImageField(upload_to='brand_logos/', blank=True, null=True,
                             help_text="The logo of the brand", verbose_name=_('Логотип'))
    categories = models.ManyToManyField(Category, related_name='brands', verbose_name=_('Категории'))

    def __str__(self):
        return f'{self.name}'

    class Meta:
        verbose_name = "Бренд"
        verbose_name_plural = "Бренды"


class Tag(models.Model):
    name = models.CharField(max_length=30, verbose_name=_('Название'))
    color = ColorField(default='#FFFFFF', null=True, verbose_name=_('Цвет'))

    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = "Теги"

    def __str__(self):
        return f'{self.name}'


class Product(models.Model):
    name = models.CharField(max_length=100, verbose_name=_('Название'))
    description = models.TextField(verbose_name=_('Описание'))
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE,
                                 verbose_name=_("Категория"))
    brand = models.ForeignKey(Brand, related_name='products', on_delete=models.PROTECT,
                              blank=True, null=True, verbose_name=_('Бренд'))
    meta_title = models.CharField(max_length=59, blank=True, null=True, verbose_name=_('Мета заголовок'))
    meta_description = models.TextField(blank=True, null=True, verbose_name=_('Мета описание'))
    meta_image = models.ImageField(upload_to='product_meta_images/', blank=True, null=True,
                                   verbose_name=_('Мета картинка'))
    keywords = models.TextField(null=True, blank=True, help_text=_('Запишите ключевые слова через запятую'), verbose_name=_('Ключевые слова'))
    min_price = models.PositiveIntegerField(default=0, verbose_name=_('Минимальная цена'))
    tags = models.ManyToManyField(Tag, blank=True, verbose_name=_('Теги'))
    is_top = models.BooleanField(default=False, verbose_name=_('Топ продукт'))
    is_new = models.BooleanField(default=False, verbose_name=_('Новый продукт'))
    sku = models.CharField(max_length=50, unique=True, blank=True, null=True, verbose_name=_('Артикул'))
    active = models.BooleanField(default=True, verbose_name=_('Активность'))
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Продукт"
        verbose_name_plural = "Продукты"


    def get_images(self):
        base_url = settings.DEFAULT_PRODUCT_URL
        images = Image.objects.filter(product=self)
        image_urls = [image.image.url for image in images if image.image]
        if not image_urls:
            image_urls = [base_url]
        return image_urls

    def save(self, *args, **kwargs):
        if not self.pk:  # Check if the instance is not yet saved
            super().save(*args, **kwargs)  # Save the instance to generate a primary key
        if not self.sku:
            self.sku = self.generate_sku()
        if not self.meta_description:
            self.meta_description = self.generate_meta_description()
        if not self.meta_title:
            self.meta_title = self.generate_meta_title()
        if not self.meta_image:
            main_image = self.images.filter(main_image=True).first()
            if main_image:
                self.meta_image = main_image.image.url
            elif self.images.exists():
                first_image = self.images.first()
                self.meta_image = first_image.image.url

        if self.variants:
            for variant in self.variants.all():
                variant.discounted_price = variant.get_price()
                variant.save()

        super().save(*args, **kwargs)

    def generate_sku(self):
        return str(uuid.uuid4()).split('-')[0]

    def generate_meta_description(self):
        if self.description:
            decoded_description = html.unescape(self.description)
            first_sentence_match = re.match(r"^(.*?[.!?])", decoded_description)
            first_sentence = first_sentence_match.group(1) if first_sentence_match else decoded_description

            return first_sentence[:160]
        else:
            return ""

    def generate_meta_title(self):
        return f'{self.name[:59]}'

    def __str__(self):
        return f'{self.name}'

    def get_popularity_score(self):
        return self.views.count()

    def get_average_rating(self):
        # Рассчитываем средний рейтинг для продукта
        average_rating = self.reviews.aggregate(Avg('rating'))['rating__avg']
        if average_rating is None:
            return 0
        return round(average_rating, 2)


class ProductView(models.Model):
    product = models.ForeignKey(Product, related_name='views', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    viewed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('product', 'user')
        verbose_name = "Просмотр продукта"
        verbose_name_plural = "Просмотры продуктов"

    def __str__(self):
        return f"{self.user} просмотрел(а) {self.product} в {self.viewed_at}"


class Characteristic(models.Model):
    key = models.CharField(max_length=255, null=True, blank=True, verbose_name=_('Ключь'))
    value = models.CharField(max_length=255, null=True, blank=True, verbose_name=_('Значение'))
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='characteristics')

    class Meta:
        verbose_name = "Характеристика"
        verbose_name_plural = "Характеристики"

    def __str__(self):
        return f'{self.key}'


class Color(models.Model):
    name = models.CharField(max_length=50, verbose_name=_('Название'))
    color = ColorField(default='#FFFFFF', verbose_name=_('Хекс'))

    class Meta:
        verbose_name = "Цвет"
        verbose_name_plural = "Цвета"

    def __str__(self):
        return f'{self.name}'


class Size(models.Model):
    name = models.CharField(max_length=50, verbose_name=_('Название'))
    description = models.CharField(max_length=100, blank=True, verbose_name=_('Описание'))
    categories = models.ManyToManyField(Category, related_name='sizes', verbose_name=_('Категории'))

    class Meta:
        verbose_name = "Размер"
        verbose_name_plural = "Размеры"

    def __str__(self):
        return f'{self.name}'


class Variant(models.Model):
    product = models.ForeignKey(Product, related_name='variants', on_delete=models.CASCADE, verbose_name=_('Продукт'))
    color = models.ForeignKey(Color, on_delete=models.PROTECT, related_name='variants', verbose_name=_('Цвет'))
    size = models.ForeignKey(Size, on_delete=models.PROTECT, related_name='variants', verbose_name=_('Размер'))
    price = models.PositiveIntegerField(default=0, verbose_name=_('Цена'))
    stock = models.PositiveIntegerField(default=0, blank=True, null=True, verbose_name=_('Количество'))
    main = models.BooleanField(default=False, verbose_name=_('Главный'))
    DISCOUNT_TYPE_CHOICES = [
        ('percent', _("Percent")),
        ('unit', _("Unit")),
    ]
    discount_value = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, help_text=_(
        "Discount amount, either in percentage or fixed unit based on the discount type."), verbose_name=_('Значение скидки'))
    discount_type = models.CharField(default=0, max_length=7, choices=DISCOUNT_TYPE_CHOICES, blank=True, null=True,
                                     help_text=_("Type of the discount - either a percent or a fixed unit."), verbose_name=_('Тмп скидки'))
    discounted_price = models.PositiveIntegerField(default=0, verbose_name=_("Цена со скидкой"), blank=True, null=True)

    class Meta:
        verbose_name = 'Вариант'
        verbose_name_plural = 'Варианты'
        indexes = [
            models.Index(fields=['price']),
            models.Index(fields=['discounted_price']),
        ]

    def __str__(self):
        return f"{self.product.name} - {self.color} - {self.size}"

    def get_price(self):
        if self.discount_value and self.discount_type:
            if self.discount_type == 'percent':
                discount_amount = (self.discount_value / 100) * self.price
                return round(self.price - discount_amount)
            elif self.discount_type == 'unit':
                return round(self.price - self.discount_value)
        return self.price


class Image(ProcessedImageModel):
    image = models.ImageField(upload_to='product_images/', verbose_name=_("Изображение"))
    small_image = models.ImageField(upload_to='product_images/', blank=True, null=True, verbose_name=_("Мини изображение"))
    main_image = models.BooleanField(default=False, verbose_name=_("Главная картинка"))
    product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE, null=True, blank=True)
    color = models.ForeignKey(Color, related_name='images', on_delete=models.PROTECT, verbose_name=_('Цвет'))

    class Meta:
        verbose_name = 'Изображение'
        verbose_name_plural = 'Изображения'

    def save(self, *args, **kwargs):
        self.process_image()
        super().save(*args, **kwargs)

    def process_image(self):
        if self.image:
            pil_image = PILImage.open(self.image)
            output_io_stream = io.BytesIO()
            pil_image.save(output_io_stream, format='WEBP', quality=90)
            output_io_stream.seek(0)
            self.image.save(f"{self.image.name.split('.')[0]}.webp", ContentFile(output_io_stream.read()), save=False)

            small_image = pil_image.copy()
            small_image.thumbnail((150, 150))
            small_output_io_stream = io.BytesIO()
            small_image.save(small_output_io_stream, format='WEBP', quality=90)
            small_output_io_stream.seek(0)
            self.small_image.save(f"{self.image.name.split('.')[0]}_small.webp", ContentFile(small_output_io_stream.read()), save=False)


class Review(models.Model):
    product = models.ForeignKey(Product, related_name='reviews', on_delete=models.CASCADE, verbose_name=_("Product"))
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_("Позьователь"))
    text = models.TextField(verbose_name=_("Текст"), blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Время создания"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Время обновления"))
    rating = models.IntegerField(default=5, choices=[(i, str(i)) for i in range(1, 6)], verbose_name=_("Рейтинг"))

    def __str__(self):
        return f"{self.created_at} by {self.user}"

    class Meta:
        verbose_name = _("Отзыв")
        verbose_name_plural = _("Отзывы")
        ordering = ["-created_at"]


class ReviewImage(ProcessedImageModel):
    review = models.ForeignKey(Review, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='review_images/')
    main_image = models.BooleanField(default=False)

    class Meta:
        verbose_name = _("Картинка отзыва")
        verbose_name_plural = _("Картинки отзывов")

    def __str__(self):
        return f"Image for {self.review}"


class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='favorites')

    class Meta:
        unique_together = ['user', 'product']

        verbose_name = _("Лайк")
        verbose_name_plural = _("Лайки")


class SizeChart(models.Model):
    categories = models.ManyToManyField(Category, related_name='size_charts', verbose_name=_("Категории"))
    name = models.CharField(max_length=100, verbose_name=_("Название"))

    class Meta:
        verbose_name = _("Карта размеров")
        verbose_name_plural = _("Карты размеров")

    def __str__(self):
        return f'{self.name}'


class SizeChartItem(models.Model):
    size_cart = models.ForeignKey(SizeChart, on_delete=models.CASCADE, verbose_name=_('Элемент карты размеров'))
    size = models.CharField(max_length=10, verbose_name=_('Размер'))

    class Meta:
        verbose_name = _("Элемент карты размеров")
        verbose_name_plural = _("Элементы карты размеров")

    def __str__(self):
        return f'{self.size}'
