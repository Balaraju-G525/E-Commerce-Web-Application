from django.core.management.base import BaseCommand
from store.models import Product

PRODUCTS = [
    ("Wireless Headphones", "Over-ear, 30h battery, noise isolation.", "2999.00", 25),
    ("Mechanical Keyboard", "Hot-swappable switches, RGB backlight.", "3499.00", 15),
    ("USB-C Hub", "7-in-1 hub with HDMI and card reader.", "1499.00", 40),
    ("Laptop Stand", "Adjustable aluminium stand.", "1199.00", 30),
    ("Webcam 1080p", "Autofocus webcam with built-in mic.", "1899.00", 20),
    ("Desk Lamp", "LED lamp with 3 colour modes.", "999.00", 35),
    ("Portable SSD 1TB", "Pocket-sized, 1000MB/s read.", "6499.00", 10),
    ("Ergonomic Mouse", "Vertical design, 6 buttons.", "1599.00", 3),
]


class Command(BaseCommand):
    help = "Insert sample products (skips if products already exist)."

    def handle(self, *args, **options):
        if Product.objects.exists():
            self.stdout.write("Products already exist - nothing to do.")
            return
        Product.objects.bulk_create(
            [Product(name=n, description=d, price=p, stock=s) for n, d, p, s in PRODUCTS])
        self.stdout.write(self.style.SUCCESS(f"Added {len(PRODUCTS)} products."))
