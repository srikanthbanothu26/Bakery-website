from django.db import models
from django.contrib.auth.models import User


class Countries(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=10)
    currency = models.CharField(max_length=10)
    currency_symbol = models.CharField(max_length=10)

    def __str__(self):
        return f"{self.name}"


class State(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True, unique=True)
    code = models.CharField(max_length=10, null=True, blank=True)
    country = models.ForeignKey('Countries', on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.name


class Bakery(models.Model):
    name = models.CharField(max_length=100)
    active = models.BooleanField(default=False)
    logo = models.ImageField(upload_to='static/images/logo/')
    instagram = models.URLField(null=True, blank=True)
    twitter = models.URLField(null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    phone = models.CharField(null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    country = models.ForeignKey('Countries', on_delete=models.CASCADE, null=True, blank=True)
    currency = models.CharField(null=True, blank=True, default='INR')
    about = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name


class UnitOfMeasurements(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class UserInfo(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    phone = models.CharField(null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    city = models.CharField(null=True, blank=True)
    pincode = models.CharField(null=True, blank=True)
    image = models.ImageField(upload_to='static/images/users', null=True, blank=True)

    def __str__(self):
        return self.user.username


class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    phone = models.CharField(null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    city = models.CharField(null=True, blank=True)
    pincode = models.CharField(null=True, blank=True)

    def __str__(self):
        return self.address
