from django.contrib import admin
from django.urls import path, include
from .views import index, create_order, payment_view, view_orders, view_order_items

urlpatterns = [
    path('pos/', index, name='pos_view'),
    path('create/pos-order/', create_order, name='create_pos_order'),
    path('payment/<int:order_id>/', payment_view, name='payment_view'),
    path('view/pos-orders/', view_orders, name='view_orders'),
    path('view/pos-order-items/<int:order_id>/', view_order_items, name='view_order_items'),
]
