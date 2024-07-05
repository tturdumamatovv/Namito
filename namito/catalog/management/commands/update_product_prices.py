from django.core.management.base import BaseCommand
from namito.catalog.models import Product


class Command(BaseCommand):
    help = 'Update price range for all products based on their variants'

    def handle(self, *args, **kwargs):
        products = Product.objects.all()
        for product in products:
            product.update_price_range()
        self.stdout.write(self.style.SUCCESS('Successfully updated price ranges for all products'))
