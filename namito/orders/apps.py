from django.apps import AppConfig


class OrdersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'namito.orders'

    def ready(self):
        import namito.orders.signals
