from django.urls import path
from .views import register, user_login, user_access, logout, view_users, view_user, create_user, update_password, \
    delete_users, send_registration_otp, resend_registration_otp, verify_registration_otp, send_otp_email, \
    create_account, send_login_otp, verify_login_otp, resend_login_otp

urlpatterns = [
    path("login/", user_login, name="user_login"),
    path("register/", register, name="user_register"),
    path("logout/", logout, name="user_logout"),
    path("user-access/", user_access, name="user_access"),
    path('view-users/', view_users, name="view_users"),
    path('view-user/<int:user_id>/', view_user, name="view_user"),
    path('create-user/', create_user, name="create_user"),
    path('update-password/<int:user_id>/', update_password, name="update_password"),
    path('users/delete/', delete_users, name='delete_users'),
    path('send-otp-mail', send_otp_email, name='send_otp_email'),
    path('verify-otp/', verify_registration_otp, name='verify_registration_otp'),
    path('send-registration_otp/', send_registration_otp, name='send_registration_otp'),
    path('resend-otp/', resend_registration_otp, name='resend_registration_otp'),
    path('create-account', create_account, name="create_account"),
    path('send-login-otp', send_login_otp, name="send_login_otp"),
    path('verify-login-otp', verify_login_otp, name="verify_login_otp"),
    path('resend-login-otp', resend_login_otp, name="resend_login_otp"),

]
