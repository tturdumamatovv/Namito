import io

from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile

from namito.catalog.models import ProcessedImageModel

from PIL import Image as PILImage


class SingletonModel(models.Model):
    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.__class__.objects.exclude(id=self.id).delete()
        super(SingletonModel, self).save(*args, **kwargs)

    @classmethod
    def load(cls):
        if not cls.objects.exists():
            cls.objects.create()
        return cls.objects.get()


# class AdminPage(SingletonModel):
#     logo = models.ImageField(upload_to='banners/', blank=True, null=True)
#     name = models.CharField(max_length=255, blank=True, null=True)
#
#     class Meta:
#         verbose_name = _('Главная страница')
#         verbose_name_plural = _("Главная страница")


class MainPage(SingletonModel):
    banner1 = models.ImageField(upload_to='banners/', blank=True, null=True)
    banner1_link = models.URLField(blank=True, null=True)
    banner2 = models.ImageField(upload_to='banners/', blank=True, null=True)
    banner2_link = models.URLField(blank=True, null=True)
    banner3 = models.ImageField(upload_to='banners/', blank=True, null=True)
    banner3_link = models.URLField(blank=True, null=True)
    title = models.CharField(verbose_name=_('Заголовок'), max_length=100, blank=True, null=True)
    description = models.TextField(verbose_name=_('Описание'), blank=True, null=True)
    counter1_title = models.CharField(max_length=30, verbose_name=_('Значение показателя 1'), blank=True, null=True)
    counter1_value = models.CharField(max_length=30, verbose_name=_('Название показателя 1'), blank=True, null=True)
    counter2_title = models.CharField(max_length=30, verbose_name=_('Значение показателя 2'), blank=True, null=True)
    counter2_value = models.CharField(max_length=30, verbose_name=_('Название показателя 2'), blank=True, null=True)
    counter3_value = models.CharField(max_length=30, verbose_name=_('Значение показателя 3'), blank=True, null=True)
    counter3_title = models.CharField(max_length=30, verbose_name=_('Название показателя 3'), blank=True, null=True)

    button_link = models.URLField(verbose_name=_('Ссылка'), blank=True, null=True)
    button = models.CharField(max_length=50, verbose_name=_('Кнопка'), blank=True, null=True)

    class Meta:
        verbose_name = _('Главная страница')
        verbose_name_plural = _("Главная страница")


class MainPageLayoutMeta(models.Model):
    meta_title = models.CharField(max_length=255, verbose_name=_('Мета Заголовок'), blank=True, null=True)
    meta_description = models.TextField(verbose_name=_('Мета Описание'), blank=True, null=True)
    meta_image = models.ImageField(upload_to='layout/meta_image', verbose_name=_('Мета Картинки'), blank=True, null=True)
    page = models.OneToOneField(MainPage, on_delete=models.CASCADE)

    class Meta:
        verbose_name = _('Мета главная страница')
        verbose_name_plural = _("Мета главная страница")


class MainPageSlider(models.Model):
    image = models.ImageField(upload_to='slider/', blank=True, null=True)
    small_image = models.ImageField(upload_to='slider-mobile/', blank=True, null=True,
                                    verbose_name=_("Мини изображение"))
    link = models.URLField(blank=True, null=True)
    page = models.ForeignKey(MainPage, on_delete=models.PROTECT, blank=True, null=True)

    class Meta:
        verbose_name = _('Слайдер')
        verbose_name_plural = _("Слайдер")

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


class StaticPage(ProcessedImageModel):
    title = models.CharField(max_length=200, unique=True, verbose_name=_('Заголовок'))
    slug = models.SlugField(max_length=200, unique=True, blank=True, verbose_name=_('Слаг'))
    content = models.TextField(verbose_name=_('Контент'))
    image = models.ImageField(upload_to='static_pages/', blank=True, null=True, verbose_name=_('Изображение'))
    meta_title = models.CharField(max_length=60, blank=True, null=True, verbose_name=_('Мета заголовок'))
    meta_description = models.CharField(max_length=160, blank=True, null=True, verbose_name=_('Мета описание'))
    meta_image = models.ImageField(upload_to='static_pages_meta/', blank=True, null=True,
                                   verbose_name=_('Мета изображение'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Время создания'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Время обновления'))

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Статичные страницы'
        verbose_name_plural = 'Статичные страницы'
        ordering = ['title']


class FAQ(models.Model):
    question = models.CharField(max_length=255, null=True, blank=True, verbose_name=_('Вопросы'))
    answer = models.TextField(null=True, blank=True, verbose_name=_('Ответы'))
    static_page = models.ForeignKey(StaticPage, on_delete=models.CASCADE, related_name='faqs')

    def clean(self):
        if not self.question and self.answer:
            raise ValidationError(_('Если указан ответ, вопрос обязателен.'))
        if not self.answer and self.question:
            raise ValidationError(_('Если указан вопрос, ответ обязателен.'))

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.question} - {self.answer}' or 'Вопрос - Ответ'

    class Meta:
        verbose_name = 'Вопрос'
        verbose_name_plural = 'Вопросы'


class Contacts(SingletonModel):
    pass
    def __str__(self):
        return 'Контактная информация'

    class Meta:
        verbose_name = 'Контакты'
        verbose_name_plural = 'Контакты'


class Phone(models.Model):
    contacts = models.ForeignKey(Contacts, on_delete=models.CASCADE)
    phone = models.CharField(max_length=100)

    def __str__(self):
        return f'{self.phone}'

    class Meta:
        verbose_name = 'Телефон'
        verbose_name_plural = 'Телефоны'


class Email(models.Model):
    contacts = models.ForeignKey(Contacts, on_delete=models.CASCADE)
    email = models.CharField(max_length=255)

    def __str__(self):
        return f'{self.email}'

    class Meta:
        verbose_name = 'Имейл'
        verbose_name_plural = 'Имейлы'


class SocialLink(models.Model):
    contacts = models.ForeignKey(Contacts, on_delete=models.CASCADE)
    link = models.CharField(max_length=100)
    icon = models.FileField(upload_to='social_icons')

    def __str__(self):
        return f'{self.link}'

    class Meta:
        verbose_name = 'Ссылка соцсети'
        verbose_name_plural = 'Ссылки соцсетей'



class Address(models.Model):
    contacts = models.ForeignKey(Contacts, on_delete=models.CASCADE)
    address = models.CharField(max_length=255)

    def __str__(self):
        return self.address

    class Meta:
        verbose_name = 'Адрес'
        verbose_name_plural = 'Адреса'


class PaymentMethod(models.Model):
    contacts = models.ForeignKey(Contacts, on_delete=models.CASCADE)
    link = models.CharField(max_length=100)
    icon = models.FileField(upload_to='payment_icons')

    def __str__(self):
        return f'{self.link}'

    class Meta:
        verbose_name = 'Ссылка оплаты'
        verbose_name_plural = 'Ссылки оплаты'

