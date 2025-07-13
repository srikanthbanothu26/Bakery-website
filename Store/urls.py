from django.urls import path
from .views import view_products_by_category, create_product_by_category, delete_product, edit_product, add_to_wishlist, \
    remove_from_wishlist, wishlist_view, add_to_cart, remove_from_carts, carts_view, view_product, \
    start_order, select_payment, place_order, get_orders, cancel_order

urlpatterns = [
    path('products/<int:category_id>', view_products_by_category, name='view_products'),
    path('products/category/<int:category_id>/create/', create_product_by_category,
         name='create_product_by_category'),
    path('product/<int:product_id>/delete/', delete_product, name='delete_product'),
    path('product/<int:product_id>/edit/', edit_product, name='edit_product'),
    path('product/<int:product_id>/add_to_wishlist/', add_to_wishlist, name='add_to_wishlist'),
    path('product/<int:product_id>/remove_from_wishlist/', remove_from_wishlist, name='remove_from_wishlist'),
    path('wishlists/', wishlist_view, name='wishlists'),
    path('add_to_cart/<int:product_id>/', add_to_cart, name='add_to_cart'),
    path('remove_from_carts/<int:product_id>/', remove_from_carts, name='remove_from_cart'),
    path('carts_view/', carts_view, name='carts'),
    path('view-product/<int:product_id>/', view_product, name='view_product'),
    path('start_order/<int:product_id>/', start_order, name='start_order'),
    path('select_payment/', select_payment, name='select_payment'),
    path('place_order/', place_order, name='place_order'),
    path('orders/', get_orders, name='orders'),
    path('cancel_order/<int:order_id>', cancel_order, name='cancel_order'),
]
