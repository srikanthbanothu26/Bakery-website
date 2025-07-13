from django.contrib import admin
from .models import Products, ProductCategory, Cart, Wishlist, Orders

admin.site.register(Products)
admin.site.register(ProductCategory)
admin.site.register(Cart)
admin.site.register(Wishlist)
admin.site.register(Orders)
