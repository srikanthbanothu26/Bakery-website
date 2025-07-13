from django.urls import include, path
from .views import home, about, user_info, edit_user_field, user_address, new_address, edit_address, delete_address, \
    save_location

urlpatterns = [
    path('', home, name='home'),
    path('about/', about, name='about'),
    path('edit-user/<str:field>/', edit_user_field, name='edit_user_field'),
    path('user_info/<int:user_id>/', user_info, name='user_info'),
    path('user/address/', user_address, name='user_address'),
    path('new_address/', new_address, name='new_address'),
    path('edit_address/<int:address_id>/', edit_address, name='edit_address'),
    path('delete_address/<int:address_id>/', delete_address, name='delete_address'),
    path('save-location/', save_location, name='save_location'),
]
