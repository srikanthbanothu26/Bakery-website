from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login as auth_login, logout as auth_logout, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from Home.models import UserInfo
from django.contrib.auth.models import User
from Home.models import Bakery
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
from Store.models import Products, ProductCategory
from django.db.models import Count


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Registration successful. Please log in.")
            return redirect('user_login')
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})


def login(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)

            user_info, created = UserInfo.objects.get_or_create(user=user)
            if created:
                print("New UserInfo created for:", user.username)
            else:
                print("Existing UserInfo found for:", user.username)

            messages.success(request, f"Welcome back, {user.username}!")
            return redirect('home')
        else:
            messages.error(request, "Invalid username or password.")
            return redirect('user_login')
    else:
        form = AuthenticationForm()

    return render(request, 'login.html', {'form': form})


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
