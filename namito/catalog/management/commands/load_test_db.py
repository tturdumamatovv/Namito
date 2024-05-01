import os
import random
import shutil

from django.core.management.base import BaseCommand
from django.db import transaction
from django.conf import settings
from faker import Faker

from namito.catalog.models import (
    Category,
    Brand,
    Tag,
    Product,
    Color,
    Size,
    Variant,
    Image,
    Characteristic
)

fake_ru = Faker('ru_RU')
fake_en = Faker()


class Command(BaseCommand):
    help = 'Generates and inserts random data into the database.'

    def handle(self, *args, **kwargs):
        with transaction.atomic():
            self.create_categories()
            self.create_brands()
            self.create_tags()
            self.create_colors()
            self.create_sizes()
            self.create_products()
            self.create_variants()
            self.stdout.write(self.style.SUCCESS('Successfully populated the database with random data.'))

    def get_random_image_path(self):
        images_path = os.path.join(settings.STATIC_ROOT, 'test_images')
        image_files = [f for f in os.listdir(images_path) if os.path.isfile(os.path.join(images_path, f))]
        return os.path.join(images_path, random.choice(image_files)) if image_files else None

    def create_categories(self):
        categories = []
        for _ in range(10):
            name = fake_en.unique.company()
            name_ru = fake_ru.unique.company()
            name_en = fake_en.unique.company()
            category = Category(
                name=name,
                name_ru=name_ru,
                name_en=name_en,
                type=random.choice([0, 1, 2, 3]),
                background_color=fake_en.hex_color(),
                order=random.randint(0, 100)
            )
            category.save()
            categories.append(category)
        return categories

    def create_brands(self):
        for _ in range(5):
            Brand.objects.create(
                name=fake_en.unique.company(),
                name_ru=fake_ru.unique.company_suffix(),
                name_en=fake_en.unique.company_suffix(),
                logo=self.get_random_image_path()
            )

    def create_tags(self):
        for _ in range(20):
            Tag.objects.create(
                name=fake_en.word(),
                name_ru=fake_ru.word(),
                name_en=fake_en.word(),
                color=fake_en.hex_color()
            )

    def create_colors(self):
        for _ in range(10):
            Color.objects.create(
                name=fake_en.color_name(),
                name_ru=fake_ru.color_name(),
                name_en=fake_en.color_name(),
                color=fake_en.hex_color()
            )

    def create_sizes(self):
        for _ in range(5):
            Size.objects.create(
                name=fake_en.word(),
                name_ru=fake_ru.word(),
                name_en=fake_en.word(),
                description=fake_en.sentence()
            )

    def create_characteristics(self):
        for _ in range(30):
            Characteristic.objects.create(
                key=fake_en.word(),
                key_ru=fake_ru.word(),
                key_en=fake_en.word(),
                value=fake_en.word(),
                value_ru=fake_ru.word(),
                value_en=fake_en.word(),

            )


    def create_products(self):
        categories = list(Category.objects.all())
        brands = list(Brand.objects.all())
        tags = list(Tag.objects.all())
        for _ in range(50):
            product = Product.objects.create(
                name=fake_en.catch_phrase(),
                name_ru=fake_ru.catch_phrase(),
                name_en=fake_en.catch_phrase(),
                description=fake_en.text(),
                description_ru=fake_ru.text(),
                description_en=fake_en.text(),
                category=random.choice(categories),
                brand=random.choice(brands),
                min_price=random.randint(100, 10000),
                is_top=fake_en.boolean(),
            )
            product.tags.set(random.sample(tags, k=random.randint(1, min(5, len(tags)))))

    def create_variants(self):
        products = list(Product.objects.all())
        colors = list(Color.objects.all())
        sizes = list(Size.objects.all())
        for product in products:
            for _ in range(3):
                variant = Variant.objects.create(
                    product=product,
                    color=random.choice(colors),
                    size=random.choice(sizes),
                    price=random.uniform(10.0, 500.0),
                    stock=random.randint(0, 100)
                )
                # Copy image file to media directory
                image_path = self.get_random_image_path()
                if image_path:
                    destination = os.path.join(settings.MEDIA_ROOT, 'product_images', os.path.basename(image_path))
                    shutil.copy(image_path, destination)
                    variant_image_path = os.path.join('product_images', os.path.basename(image_path))
                    variant_image = Image(image=variant_image_path)
                    variant_image.save()
                    variant.images.add(variant_image)
