from django.shortcuts import render, get_object_or_404, redirect
from unicodedata import category
from .models import Bakery, UserInfo, Address
from Store.models import Products, ProductCategory
from .forms import UsersForm, AddressForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
import json
import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.db.models import Count


# from .location_fetching import get_location_from_ip
# ip = request.META.get('REMOTE_ADDR')
# location = get_location_from_ip(ip)
# print(location)

def home(request):
    bakery = Bakery.objects.filter(active=True).first()
    showcase_images = Products.objects.all()
    product_categories = ProductCategory.objects.annotate(product_count=Count('products'))
    return render(request, 'home.html',
                  {'bakery': bakery, 'showcase_images': showcase_images, 'product_categories': product_categories})


def about(request):
    bakery = Bakery.objects.filter(active=True).first()
    product_categories = ProductCategory.objects.annotate(product_count=Count('products'))
    return render(request, 'about.html', {'bakery': bakery, 'product_categories': product_categories})


@login_required
def user_info(request, user_id):
    bakery = Bakery.objects.filter(active=True).first()
    product_categories = ProductCategory.objects.annotate(product_count=Count('products'))

    user = get_object_or_404(User, id=user_id)
    user_profile = get_object_or_404(UserInfo, user=user)

    return render(request, 'user_info.html', {
        'bakery': bakery,
        'current_user': user_profile,
        'product_categories': product_categories,
    })


from django.forms import modelform_factory


@login_required
def edit_user_field(request, field):
    product_categories = ProductCategory.objects.annotate(product_count=Count('products'))

    bakery = Bakery.objects.filter(active=True).first()
    user_profile = get_object_or_404(UserInfo, user=request.user)

    editable_fields = ['name', 'email', 'phone', 'address', 'city', 'pincode', 'image']
    if field not in editable_fields:
        raise Http404("This field cannot be edited.")

    UserFieldForm = modelform_factory(UserInfo, fields=[field])

    if request.method == 'POST':
        form = UserFieldForm(request.POST, request.FILES, instance=user_profile)
        if form.is_valid():
            form.save()
            return redirect('user_info', user_id=user_profile.user.id)
    else:
        form = UserFieldForm(instance=user_profile)

    form.fields[field].widget.attrs.update({
        'class': 'w-full border-b-2 border-gray-300 focus:border-blue-500 transition p-2 outline-none bg-white dark:bg-gray-900 text-black dark:text-white',
        'id': 'form_field'
    })

    return render(request, 'edit_user_field.html', {
        'form': form,
        'form_field': form[field],
        'field_label': field.capitalize(),
        'user_profile': user_profile,
        'bakery': bakery,
        'product_categories': product_categories,
    })


def user_address(request):
    bakery = Bakery.objects.filter(active=True).first()
    address = Address.objects.filter(user=request.user)
    product_categories = ProductCategory.objects.annotate(product_count=Count('products'))

    return render(request, 'user_address.html', {
        'bakery': bakery,
        'address': address,
        'product_categories': product_categories,
    })


def new_address(request):
    bakery = Bakery.objects.filter(active=True).first()
    product_categories = ProductCategory.objects.annotate(product_count=Count('products'))

    if request.method == 'POST':
        form = AddressForm(request.POST, request.FILES)
        if form.is_valid():
            new_address = form.save(commit=False)
            new_address.user = request.user
            new_address.save()
            return redirect('user_address')
    else:
        form = AddressForm()  # No instance needed for new address

    return render(request, 'new_address.html',
                  {'bakery': bakery, 'form': form, 'product_categories': product_categories})


def edit_address(request, address_id):
    bakery = Bakery.objects.filter(active=True).first()
    address = get_object_or_404(Address, id=address_id)
    product_categories = ProductCategory.objects.annotate(product_count=Count('products'))

    if request.method == 'POST':
        form = AddressForm(request.POST, request.FILES, instance=address)
        if form.is_valid():
            edited_address = form.save(commit=False)
            edited_address.user = request.user
            edited_address.save()
            return redirect('user_address')
    else:
        form = AddressForm(instance=address)
    return render(request, 'edit_address.html',
                  {'bakery': bakery, 'form': form, 'product_categories': product_categories})


def delete_address(request, address_id):
    address = get_object_or_404(Address, id=address_id)
    address.delete()
    return redirect('user_address')


@csrf_exempt
@require_http_methods(["POST"])
def save_location(request):
    try:
        data = json.loads(request.body)
        lat = data.get("latitude")
        lon = data.get("longitude")

        if lat and lon:
            # Reverse geocode using OpenStreetMap Nominatim
            url = f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=json"
            headers = {'User-Agent': 'MyDjangoApp/1.0'}
            response = requests.get(url, headers=headers, timeout=5)

            if response.status_code == 200:
                location_data = response.json()
                address = location_data.get("address", {})

                request.session['user_lat'] = lat
                request.session['user_lon'] = lon
                request.session['user_city'] = address.get("city") or address.get("town") or address.get("village")
                request.session['user_postcode'] = address.get("postcode")
                request.session['user_street'] = address.get("road")
                request.session['user_state'] = address.get("state")
                request.session['user_country'] = address.get("country")
                request.session['user_neighbourhood'] = address.get("neighbourhood")
                request.session['user_suburb'] = address.get("suburb")
                request.session['user_city_district'] = address.get("city_district")
                request.session['user_county'] = address.get("county")
                request.session['user_state_district'] = address.get("state_district")

                return JsonResponse({'status': 'success', 'address': address})
            else:
                return JsonResponse({'status': 'failed', 'reason': 'Geocoding error'}, status=500)

        return JsonResponse({'status': 'invalid request'}, status=400)

    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'reason': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'status': 'error', 'reason': str(e)}, status=500)
