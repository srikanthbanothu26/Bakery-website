from django.db import models
from django.contrib.auth.models import User
from Home.models import *
from django.utils import timezone


class ProductCategory(models.Model):
    name = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name


class Products(models.Model):
    weights = [
        ('250gm', '250 GM'),
        ('500gm', '500 GM'),
        ('1kg', '1 KGM'),
        ('1500gm', '1500 GM'),
        ('2kg', '2 KGM'),
    ]
    name = models.CharField(null=True, blank=True, max_length=400)
    image = models.ImageField(null=True, blank=True, upload_to='static/images/products/')
    price = models.FloatField(null=True, blank=True)
    category = models.ForeignKey(ProductCategory, on_delete=models.CASCADE, null=True, blank=True,
                                 related_name='products')
    weight = models.CharField(choices=weights, default='1kg', max_length=100)

    def __str__(self):
        return self.name


class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    product = models.ForeignKey(Products, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.product.name


class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    product = models.ForeignKey(Products, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.product.name


class Orders(models.Model):
    status_choices = [
        ('draft', 'Draft'),
        ('confirm', 'Confirmed'),
        ('cancel', 'Cancelled'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    product = models.ForeignKey(Products, on_delete=models.SET_NULL, null=True, blank=True)
    address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True, blank=True)
    total_amount = models.FloatField(null=True, blank=True)
    weight = models.CharField(max_length=20, null=True, blank=True)
    reference = models.CharField(max_length=20, blank=True, null=True, unique=True)
    order_date = models.DateTimeField(blank=True, null=True)
    status = models.BooleanField(default=False)
    order_state = models.CharField(choices=status_choices, max_length=20, null=True, blank=True, default="draft")
    quantity = models.CharField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.reference:
            year = timezone.now().year
            count = Orders.objects.filter(reference__startswith=f"SO/{year}/").count() + 1
            self.reference = f"SO/{year}/{count:05d}"

        if self.status and self.order_state == 'draft':
            self.order_state = 'confirm'

        super().save(*args, **kwargs)

        if not self.status and self.order_state != 'cancel':
            from Store.tasks import mark_order_status_true
            mark_order_status_true.apply_async((self.id,), countdown=300)

    def __str__(self):
        username = self.user.username if self.user else "Guest"
        return f"{self.reference} - {username}"

    def get_order_state_display_value(self):
        return dict(self.status_choices).get(self.order_state, self.order_state)
