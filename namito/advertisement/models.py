from django.db import models
from django.utils.translation import gettext_lazy as _

from namito.pages.models import MainPage
from namito.users.models import User


class Advertisement(models.Model):
    image = models.FileField(upload_to='banners/', verbose_name='Картинка', blank=True, null=True)
    title = models.CharField(max_length=30, verbose_name='Заголовок', blank=True, null=True)
    description = models.CharField(max_length=100, verbose_name='Описание', blank=True, null=True)
    button_link = models.URLField(verbose_name='Ссылка', blank=True, null=True)
    button = models.CharField(max_length=30, verbose_name='Кнопка', blank=True, null=True)
    page = models.ForeignKey(MainPage, on_delete=models.PROTECT, blank=True, null=True)

    class Meta:
        verbose_name = _('Рекламу')
        verbose_name_plural = _('Рекламы')

    def __str__(self):
        return f'{self.title}'


class Notification(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to='notifications/')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications', blank=True, null=True)

    def __str__(self):
        return self.title
