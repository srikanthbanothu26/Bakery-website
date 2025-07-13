from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now
from Store.models import Products, ProductCategory


class Order(models.Model):
    reference = models.CharField(max_length=20, unique=True, editable=False, null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(default=now, null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.reference:
            year = now().year
            count = Order.objects.filter(created_at__year=year).count() + 1
            self.reference = f"POS/{year}/{str(count).zfill(5)}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.reference


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Products, on_delete=models.PROTECT, null=True, blank=True)
    quantity = models.FloatField(null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.product.name} (x{self.quantity})"


class Payment(models.Model):
    PAYMENT_METHODS = [
        ('cash', 'Cash'),
    ]

    order = models.OneToOneField(Order, on_delete=models.CASCADE, null=True, blank=True)
    method = models.CharField(max_length=20, choices=PAYMENT_METHODS, default="cash")
    paid = models.BooleanField(default=False)
    paid_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Payment for {self.order.reference} - {self.get_method_display()}"
