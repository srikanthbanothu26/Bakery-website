from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login as auth_login, logout as auth_logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from Home.models import Bakery,UserInfo
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
import json
from Store.models import Products, ProductCategory
from django.db.models import Count
import random
import time

import string
import secrets
from threading import Thread
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import render
from django.core.mail import send_mail
from django.conf import settings
from .forms import RegisterForm, LoginForm  # Ensure proper relative import

OTP_EXPIRY_SECONDS = 300  # Extended to 5 minutes to accommodate real-world network latency


def generate_password(length=16):
    lowercase = string.ascii_lowercase
    uppercase = string.ascii_uppercase
    digits = string.digits
    symbols = "!@#$%^&*()-_=+"
    chars = lowercase + uppercase + digits + symbols
    while True:
        password = ''.join(secrets.choice(chars) for _ in range(length))
        if (any(c.islower() for c in password) and
                any(c.isupper() for c in password) and
                any(c.isdigit() for c in password) and
                any(c in symbols for c in password)):
            return password


def send_otp_email(email, otp):
    company = Bakery.objects.filter(active=True).first()
    company_name = company.name if company else "Vanguard Automotive"

    html_message = f"""
    <div style="font-family: Arial, sans-serif; line-height: 1.6; color: #333333; max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #e0e0e0; border-radius: 8px;">
        <h2 style="color: #1a56db; margin-top: 0;">Sign-in Verification</h2>
        <p>Hello,</p>
        <p>We received a request to sign in to your <strong>{company_name}</strong> account.</p>
        <p>Your One-Time Password (OTP) is:</p>
        <div style="margin: 24px 0; text-align: center;">
            <span style="font-size: 32px; font-weight: bold; letter-spacing: 6px; color: #111827; background-color: #f3f4f6; padding: 12px 24px; border-radius: 8px; border: 1px dashed #9ca3af; display: inline-block;">
                {otp}
            </span>
        </div>
        <p style="color: #dc2626; font-weight: 500;">
            This OTP is valid for the next 5 minutes.
        </p>
        <hr style="border: 0; border-top: 1px solid #e5e7eb; margin: 24px 0;" />
        <p style="font-size: 13px; color: #6b7280;">
            If you did not request this verification code, please ignore this email safely.
        </p>
        <p style="font-size: 14px; color: #4b5563; margin-bottom: 0;">
            Thank you,<br><strong>{company_name} Team</strong>
        </p>
    </div>
    """

    plain_message = f"""Hello,\n\nWe received a request to sign in to your {company_name} account.\n\nYour One-Time Password (OTP) is: {otp}\n\nThis OTP is valid for the next 5 minutes.\n\nIf you did not request this verification code, please ignore this email.\n\nThank you,\n{company_name} Team"""

    try:
        send_mail(
            subject=f"{company_name} Verification Code",
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            html_message=html_message,
            fail_silently=False,
        )
    except Exception as e:
        # In staging/production use a logger: logger.error(f"Email Error: {e}")
        print("Email Error:", e)


def send_registration_otp(request):
    if request.method != "POST":
        return JsonResponse({"success": False, "message": "Invalid request method."})

    email = request.POST.get("email", "").strip().lower()
    if not email:
        return JsonResponse({"success": False, "message": "Email is required."})

    if User.objects.filter(email=email).exists():
        return JsonResponse({"success": False, "message": "Email already registered."})

    otp = str(random.randint(100000, 999999))

    # Standardize session keys across registration flows
    request.session["registration_email"] = email
    request.session["registration_otp"] = otp
    request.session["registration_created_at"] = time.time()
    request.session["email_verified"] = False
    request.session.modified = True

    # Note: Threads drop execution if the WSGI process Recycles. Consider Celery tasks here instead.
    Thread(target=send_otp_email, args=(email, otp), daemon=True).start()

    return JsonResponse({"success": True, "message": "Verification code sent successfully."})


def resend_registration_otp(request):
    email = request.session.get("registration_email")
    if not email:
        return JsonResponse({"success": False, "message": "Session expired or invalid."})

    otp = str(random.randint(100000, 999999))
    request.session["registration_otp"] = otp
    request.session["registration_created_at"] = time.time()
    request.session.modified = True

    Thread(target=send_otp_email, args=(email, otp), daemon=True).start()

    return JsonResponse({"success": True, "message": "OTP sent again."})


def verify_registration_otp(request):
    if request.method != "POST":
        return JsonResponse({"success": False, "message": "Invalid request method."})

    entered_otp = request.POST.get("otp", "").strip()
    actual_otp = request.session.get("registration_otp")
    created_at = request.session.get("registration_created_at")

    if not actual_otp or not created_at:
        return JsonResponse({"success": False, "message": "OTP session expired."})

    if time.time() - created_at > OTP_EXPIRY_SECONDS:
        return JsonResponse({"success": False, "message": "OTP expired."})

    if entered_otp != actual_otp:
        return JsonResponse({"success": False, "message": "Incorrect OTP."})

    # Mark email verification step as successful
    request.session["email_verified"] = True
    request.session.modified = True

    return JsonResponse({
        "success": True,
        "message": "Email verified successfully. Proceed to profile completion."
    })


def create_account(request):
    if request.method != "POST":
        return JsonResponse({"success": False, "message": "Invalid request method."})

    if not request.session.get("email_verified"):
        return JsonResponse({"success": False, "message": "Please verify your email first."})

    email = request.session.get("registration_email")
    mobile = request.POST.get("mobile", "").strip()

    if not mobile:
        return JsonResponse({"success": False, "message": "Mobile number is required."})

    if not email:
        return JsonResponse({"success": False, "message": "Session missing vital email reference."})

    if User.objects.filter(email=email).exists():
        return JsonResponse({"success": False, "message": "User with this email already exists."})

    # Create account safely
    password = generate_password()
    user = User.objects.create_user(
        username=email,
        email=email,
        password=password
    )

    # Set custom properties safely if they exist on your custom/extended user model
    if hasattr(user, "mobile"):
        user.mobile = mobile
        user.save()

    # Dynamic branding for credential email template
    company = Bakery.objects.filter(active=True).first()
    company_name = company.name if company else "Vanguard Automotive"

    send_mail(
        subject=f"Your {company_name} Login Credentials",
        message=f"Welcome!\n\nYour account has been created.\n\nUsername: {email}\nPassword: {password}\n\nPlease login and change your password immediately.",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[email],
        fail_silently=False,
    )

    # Auto log the user in to drop registration conversion drop-off
    login(request, user)

    # Flush complete step session variables cleanly
    registration_session_keys = [
        "registration_email",
        "registration_otp",
        "registration_created_at",
        "email_verified"
    ]
    for key in registration_session_keys:
        request.session.pop(key, None)
    request.session.modified = True

    return JsonResponse({
        "success": True,
        "redirect_url": "/"
    })


def register(request):
    company = Bakery.objects.filter(active=True).first()
    return render(
        request,
        "register.html",
        {
            "company": company,
            "form": RegisterForm(),
        },
    )

def user_login(request):
    if request.user.is_authenticated:
        # user_info = UserInfo.objects.filter(user=request.user).first()
        #
        # if not user_info:
        #     UserInfo.objects.create(user=request.user)

        return redirect("home")

    company = Bakery.objects.filter(active=True).first()

    return render(
        request,
        "login.html",
        {
            "company": company,
            "form": LoginForm(),
        },
    )

def send_login_otp(request):
    if request.method != "POST":
        return JsonResponse({
            "success": False,
            "message": "Invalid request."
        })
    email = request.POST.get("email", "").strip().lower()
    if not email:
        return JsonResponse({
            "success": False,
            "message": "Email is required."
        })
    try:
        User.objects.get(email=email)
    except User.DoesNotExist:
        return JsonResponse({
            "success": False,
            "message": "No account found with this email."
        })

    otp = str(random.randint(100000, 999999))

    request.session["login_email"] = email
    request.session["login_otp"] = otp
    request.session["otp_created_at"] = time.time()
    request.session.modified = True

    Thread(
        target=send_otp_email,
        args=(email, otp),
        daemon=True,
    ).start()

    return JsonResponse({
        "success": True,
        "message": "Verification code sent.",
        "expires_in": 45,
    })


def verify_login_otp(request):
    if request.method != "POST":
        return JsonResponse({
            "success": False,
            "message": "Invalid request."
        })
    entered_otp = request.POST.get("otp", "").strip()
    email = request.session.get("login_email")
    session_otp = request.session.get("login_otp")
    otp_created_at = request.session.get("otp_created_at")

    if not email:
        return JsonResponse({
            "success": False,
            "message": "Session expired."
        })

    if not session_otp:
        return JsonResponse({
            "success": False,
            "message": "OTP expired."
        })

    if time.time() - otp_created_at > 45:
        request.session.pop("login_otp", None)
        request.session.pop("otp_created_at", None)

        return JsonResponse({
            "success": False,
            "expired": True,
            "message": "OTP expired."
        })

    if entered_otp != session_otp:
        return JsonResponse({
            "success": False,
            "message": "Invalid OTP."
        })

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return JsonResponse({
            "success": False,
            "message": "User not found."
        })

    login(request, user)

    request.session.pop("login_email", None)
    request.session.pop("login_otp", None)
    request.session.pop("otp_created_at", None)

    return JsonResponse({
        "success": True,
        "redirect_url": "/"
    })


def resend_login_otp(request):
    if request.method != "POST":
        return JsonResponse({
            "success": False,
            "message": "Invalid request."
        })

    email = request.session.get("login_email")

    if not email:
        return JsonResponse({
            "success": False,
            "message": "Session expired."
        })

    otp = str(random.randint(100000, 999999))

    request.session["login_otp"] = otp
    request.session["otp_created_at"] = time.time()
    request.session.modified = True

    Thread(
        target=send_otp_email,
        args=(email, otp),
        daemon=True,
    ).start()

    return JsonResponse({
        "success": True,
        "message": "OTP resent successfully.",
        "expires_in": 45,
    })


def logout(request):
    auth_logout(request)
    return redirect('home')


@login_required(login_url='user_login')
def user_access(request):
    bakery = Bakery.objects.filter(active=True).first()
    users = User.objects.all().order_by('id')

    if request.method == 'POST':
        for user in users:
            user_id = user.id
            user.username = request.POST.get(f'user_{user_id}_username', user.username)
            user.email = request.POST.get(f'user_{user_id}_email', user.email)
            user.first_name = request.POST.get(f'user_{user_id}_first_name', user.first_name)
            user.last_name = request.POST.get(f'user_{user_id}_last_name', user.last_name)
            user.is_active = f'user_{user_id}_is_active' in request.POST
            user.is_staff = f'user_{user_id}_is_staff' in request.POST
            user.is_superuser = f'user_{user_id}_is_superuser' in request.POST
            new_password = request.POST.get(f'user_{user_id}_password')
            if f'user_{user_id}_update_password' in request.POST and new_password:
                user.set_password(new_password)
            user.save()
        return redirect('user_access')  # Change to your actual URL name

    return render(request, 'user_access.html', {
        'users': users,
        'bakery': bakery
    })


def view_users(request):
    users = User.objects.all().order_by('id')
    bakery = Bakery.objects.filter(active=True).first()
    product_categories = ProductCategory.objects.annotate(product_count=Count('products'))
    return render(request, 'view_users.html',
                  {'users': users, 'bakery': bakery, 'product_categories': product_categories})


def create_user(request):
    bakery = Bakery.objects.filter(active=True).first()
    product_categories = ProductCategory.objects.annotate(product_count=Count('products'))
    if request.method == 'POST':
        username = request.POST.get('username')
        is_staff = bool(request.POST.get('is_staff'))
        is_superuser = bool(request.POST.get('is_superuser'))
        is_active = bool(request.POST.get('is_active'))

        user = User.objects.create_user(username=username)
        user.is_staff = is_staff
        user.is_superuser = is_superuser
        user.is_active = is_active
        user.save()
        return redirect('view_users')
    return render(request, 'create_user.html', {'bakery': bakery, 'product_categories': product_categories})


def view_user(request, user_id):
    bakery = Bakery.objects.filter(active=True).first()
    user_obj = get_object_or_404(User, id=user_id)
    product_categories = ProductCategory.objects.annotate(product_count=Count('products'))
    if request.method == 'POST':
        user_obj.username = request.POST.get('username')
        user_obj.is_staff = bool(request.POST.get('is_staff'))
        user_obj.is_superuser = bool(request.POST.get('is_superuser'))
        user_obj.is_active = bool(request.POST.get('is_active'))
        user_obj.save()
        return redirect('view_user', user_id=user_obj.id)
    return render(request, 'create_user.html',
                  {'user_obj': user_obj, 'bakery': bakery, 'product_categories': product_categories})


def update_password(request, user_id):
    if request.method == 'POST':
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        if new_password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect('edit_user', user_id=user_id)

        user = get_object_or_404(User, id=user_id)
        user.set_password(new_password)
        user.save()
        messages.success(request, "Password changed successfully.")
        return redirect('view_users')


@csrf_exempt
def delete_users(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        ids = data.get('ids', [])
        User.objects.filter(id__in=ids).delete()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'error': 'Invalid request'}, status=400)
