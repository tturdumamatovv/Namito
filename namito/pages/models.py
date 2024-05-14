from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from namito.catalog.models import ProcessedImageModel


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


class MainPageSlider(models.Model):
    title = models.CharField(max_length=100, verbose_name=_('Загловок'), blank=True, null=True)
    description = models.CharField(max_length=100, verbose_name=_('Описание'), blank=True, null=True)
    image = models.ImageField(upload_to='slider/', blank=True, null=True)
    link = models.URLField(blank=True, null=True)
    page = models.ForeignKey(MainPage, on_delete=models.PROTECT, blank=True, null=True)

    class Meta:
        verbose_name = _('Слайдер')
        verbose_name_plural = _("Слайдер")


class StaticPage(ProcessedImageModel):
    title = models.CharField(max_length=200, unique=True, verbose_name=_('Заголовок'))
    slug = models.SlugField(max_length=200, unique=True, blank=True, verbose_name=_('Слаг'))
    content = models.TextField(verbose_name=_('Контент'))
    image = models.ImageField(upload_to='static_pages/', blank=True, null=True, verbose_name=_('Изображение'))
    meta_title = models.CharField(max_length=60, blank=True, null=True, verbose_name=_('Мета заголовок'))
    meta_description = models.CharField(max_length=160, blank=True, null=True, verbose_name=_('Мета описание'))
    meta_image = models.ImageField(upload_to='static_pages_meta/', blank=True, null=True, verbose_name=_('Мета описание'))
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
