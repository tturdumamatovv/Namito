import random

from faker import Faker

from django.core.management.base import BaseCommand
from django.db import transaction

from namito.catalog.models import (
    Category,
    Brand,
    Tag,
    Product,
    Color,
    Size,
    Variant
)

fake = Faker()


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

    def create_categories(self):
        categories = []
        for _ in range(10):
            name = fake.unique.company()
            category = Category(
                name=name,
                type=random.choice([0, 1, 2, 3]),
                background_color=fake.hex_color(),
                order=random.randint(0, 100)
            )
            category.save()
            categories.append(category)
        return categories

    def create_brands(self):
        for _ in range(5):
            Brand.objects.create(
                name=fake.unique.company(),
                logo=fake.image_url()
            )

    def create_tags(self):
        for _ in range(20):
            Tag.objects.create(
                name=fake.word(),
                color=fake.hex_color()
            )

    def create_colors(self):
        for _ in range(10):
            Color.objects.create(
                name=fake.color_name(),
                color=fake.hex_color()
            )

    def create_sizes(self):
        for _ in range(5):
            Size.objects.create(
                name=fake.word(),
                description=fake.sentence()
            )

    def create_products(self):
        categories = list(Category.objects.all())
        brands = list(Brand.objects.all())
        tags = list(Tag.objects.all())
        for _ in range(50):
            product = Product.objects.create(
                name=fake.catch_phrase(),
                description=fake.text(),
                category=random.choice(categories),
                brand=random.choice(brands),
                min_price=random.randint(100, 10000),
                is_top=fake.boolean()
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
                # Optionally create an image for each variant
                # Image.objects.create(
                #     image=fake.image_url(),
                #     main_image=fake.boolean(),
                #     variant=variant
                # )
