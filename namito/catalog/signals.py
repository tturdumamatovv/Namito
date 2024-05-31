from django.db.models.signals import m2m_changed
from django.dispatch import receiver

from namito.catalog.models import Brand, Size


@receiver(m2m_changed, sender=Brand.categories.through)
def update_brand_child_categories(sender, instance, action, **kwargs):
    if action == 'post_add' or action == 'post_remove':
        categories_to_update = set()
        for category in instance.categories.all():
            categories_to_update.update(category.get_descendants(include_self=True))
        instance.categories.set(categories_to_update)


@receiver(m2m_changed, sender=Size.categories.through)
def update_size_child_categories(sender, instance, action, **kwargs):
    if action == 'post_add' or action == 'post_remove':
        categories_to_update = set()
        for category in instance.categories.all():
            categories_to_update.update(category.get_descendants(include_self=True))
        instance.categories.set(categories_to_update)
