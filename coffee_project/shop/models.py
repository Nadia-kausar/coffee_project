from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal
from django.core.validators import MinValueValidator

class Product(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.00'))])
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='product_images/', null=True, blank=True)

    def __str__(self):
        return self.name

class Order(models.Model):
    STATUS_CART = 'cart'
    STATUS_PLACED = 'placed'

    STATUS_CHOICES = [
        (STATUS_CART, 'Cart'),
        (STATUS_PLACED, 'Placed'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    created_at = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_CART)

    def __str__(self):
        return f"Order #{self.id} by {self.user.username} ({self.status})"

    def calculate_total(self):
        total = sum(item.total_price for item in self.items.all())
        self.total = total
        self.save()

    def add_product(self, product, quantity=1):
        order_item, created = OrderItem.objects.get_or_create(order=self, product=product)
        if not created:
            order_item.quantity += quantity
        else:
            order_item.quantity = quantity
        order_item.save()
        self.calculate_total()

    def update_item_quantity(self, product, quantity):
        try:
            order_item = self.items.get(product=product)
            if quantity <= 0:
                order_item.delete()
            else:
                order_item.quantity = quantity
                order_item.save()
            self.calculate_total()
        except OrderItem.DoesNotExist:
            pass

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.product.name} (Order #{self.order.id})"

    @property
    def total_price(self):
        return self.product.price * self.quantity
