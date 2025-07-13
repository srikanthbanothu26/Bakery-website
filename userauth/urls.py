from django.urls import path
from .views import register, login, user_access, logout, view_users, view_user, create_user, update_password, \
    delete_users

urlpatterns = [
    path("login/", login, name="user_login"),
    path("register/", register, name="user_register"),
    path("logout/", logout, name="user_logout"),
    path("user-access/", user_access, name="user_access"),
    path('view-users/', view_users, name="view_users"),
    path('view-user/<int:user_id>/', view_user, name="view_user"),
    path('create-user/', create_user, name="create_user"),
    path('update-password/<int:user_id>/', update_password, name="update_password"),
    path('users/delete/', delete_users, name='delete_users'),

]
