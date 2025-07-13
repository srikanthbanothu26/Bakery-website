from django.shortcuts import render, redirect, get_object_or_404
from .models import Products, ProductCategory, Wishlist, Cart, Orders
from .forms import ProductForm
from Home.models import Bakery, Address
from django.http import HttpResponse, JsonResponse
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from Home.forms import AddressForm
from django.utils import timezone


@login_required(login_url='user_login')
def view_products_by_category(request, category_id):
    product_categories = ProductCategory.objects.all()
    category = get_object_or_404(ProductCategory, id=category_id)
    bakery = Bakery.objects.filter(active=True).first()

    search_query = request.GET.get('search', '')
    products = Products.objects.filter(category=category)
    if search_query:
        products = products.filter(Q(name__icontains=search_query))

    wishlist_product_ids = Wishlist.objects.filter(user=request.user).values_list('product', flat=True)
    cart_product_ids = Cart.objects.filter(user=request.user).values_list('product', flat=True)

    return render(request, 'view_products.html', {
        'products': products,
        'category': category,
        'bakery': bakery,
        'wishlist_product_ids': wishlist_product_ids,
        'cart_product_ids': cart_product_ids,
        'product_categories': product_categories,
        'search_query': search_query,
    })


@login_required(login_url='user_login')
def create_product_by_category(request, category_id):
    category = get_object_or_404(ProductCategory, pk=category_id)
    bakery = Bakery.objects.filter(active=True).first()
    product_categories = ProductCategory.objects.all()
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.category = category
            product.save()
            return redirect('view_products', category_id=category.id)
    else:
        form = ProductForm()

    return render(request, 'create_product.html',
                  {'form': form, 'category': category, 'bakery': bakery, 'product_categories': product_categories})


@login_required(login_url='user_login')
def edit_product(request, product_id):
    product = get_object_or_404(Products, id=product_id)
    bakery = Bakery.objects.filter(active=True).first()
    product_categories = ProductCategory.objects.all()

    form = ProductForm(request.POST or None, request.FILES or None, instance=product)

    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('view_products', category_id=product.category.id)

    return render(request, 'edit_product.html', {
        'form': form,
        'edit': True,
        'bakery': bakery,
        'product_categories': product_categories,
    })


@login_required(login_url='user_login')
def delete_product(request, product_id):
    product = get_object_or_404(Products, id=product_id)
    product.delete()
    return redirect('view_products', category_id=product.category.id)


@login_required(login_url='user_login')
def view_product(request, product_id):
    product = get_object_or_404(Products, id=product_id)
    bakery = Bakery.objects.filter(active=True).first()
    wishlist_product_ids = Wishlist.objects.filter(user=request.user).values_list('product', flat=True)
    cart_product_ids = Cart.objects.filter(user=request.user).values_list('product', flat=True)
    product_categories = ProductCategory.objects.all()
    return render(request, 'view_product.html', {'product': product, 'wishlist_product_ids': wishlist_product_ids,
                                                 'cart_product_ids': cart_product_ids, 'bakery': bakery,
                                                 'product_categories': product_categories, })


@login_required(login_url='user_login')
def add_to_wishlist(request, product_id):
    product = get_object_or_404(Products, id=product_id)

    # Check if this product is already in the user's wishlist
    if Wishlist.objects.filter(user=request.user, product=product).exists():
        return JsonResponse({
            'status': 'exists',
            'message': f'{product.name} is already in your wishlist'
        })

    Wishlist.objects.create(user=request.user, product=product)
    return JsonResponse({
        'status': 'added',
        'message': f'{product.name} added to your wishlist'
    })


@login_required(login_url='user_login')
def remove_from_wishlist(request, product_id):
    product = get_object_or_404(Products, id=product_id)
    deleted, _ = Wishlist.objects.filter(user=request.user, product=product).delete()
    if deleted:
        return JsonResponse({'status': 'removed', 'message': f'{product.name} removed from wishlist'})
    return JsonResponse({'status': 'not_found', 'message': f'{product.name} not found in wishlist'})


@login_required(login_url='user_login')
def add_to_cart(request, product_id):
    product = get_object_or_404(Products, id=product_id)
    if not Cart.objects.filter(user=request.user, product=product).exists():
        Cart.objects.create(user=request.user, product=product)
        return JsonResponse({'status': 'added', 'message': f'{product.name} added to cart'})
    return JsonResponse({'status': 'exists', 'message': f'{product.name} is already in cart'})


@login_required(login_url='user_login')
def remove_from_carts(request, product_id):
    product = get_object_or_404(Products, id=product_id)
    deleted, _ = Cart.objects.filter(user=request.user, product=product).delete()
    if deleted:
        return JsonResponse({'status': 'removed', 'message': f'{product.name} removed from cart'})
    return JsonResponse({'status': 'not_found', 'message': f'{product.name} not found in cart'})


@login_required(login_url='user_login')
def wishlist_view(request):
    product_categories = ProductCategory.objects.all()
    wishlists = Wishlist.objects.filter(user=request.user)
    bakery = Bakery.objects.filter(active=True).first()
    return render(request, 'wishlist_view.html',
                  {'wishlists': wishlists, 'bakery': bakery, 'product_categories': product_categories, })


@login_required(login_url='user_login')
def carts_view(request):
    product_categories = ProductCategory.objects.all()
    carts = Cart.objects.filter(user=request.user)
    bakery = Bakery.objects.filter(active=True).first()
    return render(request, 'carts_view.html',
                  {'carts': carts, 'bakery': bakery, 'product_categories': product_categories, })


@login_required(login_url='user_login')
def start_order(request, product_id):
    product_categories = ProductCategory.objects.all()
    bakery = Bakery.objects.filter(active=True).first()
    product = get_object_or_404(Products, id=product_id)
    quantity = float(request.POST.get("quantity") or 1)
    selected_weight = request.POST.get("weight")
    weight_multiplier = {
        '250gm': 0.25,
        '500gm': 0.5,
        '1kg': 1,
        '1500gm': 1.5,
        '2kg': 2
    }.get(selected_weight, 1)
    total_amount = product.price * weight_multiplier * quantity
    addresses = Address.objects.filter(user=request.user)
    form = AddressForm()

    if request.method == 'POST' and 'add_address' in request.POST:
        form = AddressForm(request.POST)
        if form.is_valid():
            new_address = form.save(commit=False)
            new_address.user = request.user
            new_address.save()
            addresses = Address.objects.filter(user=request.user)
            form = AddressForm()

    return render(request, "select_address.html", {
        'product': product,
        'quantity': quantity,
        'weight': selected_weight,
        'total_amount': total_amount,
        'addresses': addresses,
        'form': form,
        'bakery': bakery,
        'product_categories': product_categories,
    })


@login_required(login_url='user_login')
def select_payment(request):
    bakery = Bakery.objects.filter(active=True).first()
    product_categories = ProductCategory.objects.all()

    if request.method == 'POST':
        product_id = request.POST.get("product_id")
        quantity = float(request.POST.get("quantity"))
        total_amount = float(request.POST.get("total_amount"))
        address_id = request.POST.get("address_id")
        selected_weight = request.POST.get("weight", "1kg")

        product = get_object_or_404(Products, id=product_id)
        address = get_object_or_404(Address, id=address_id)

        return render(request, "payment_method.html", {
            'product': product,
            'quantity': quantity,
            'total_amount': total_amount,
            'address': address,
            'weight': selected_weight,
            'bakery': bakery,
            'product_categories': product_categories,
        })


@login_required(login_url='user_login')
def place_order(request):
    bakery = Bakery.objects.filter(active=True).first()
    product_categories = ProductCategory.objects.all()

    if request.method == 'POST':
        product = get_object_or_404(Products, id=request.POST['product_id'])
        address = get_object_or_404(Address, id=request.POST['address_id'])
        total_amount = float(request.POST.get('total_amount', 0.0))
        selected_weight = request.POST.get('weight', '1kg')
        quantity = float(request.POST.get("quantity"))

        Orders.objects.create(
            user=request.user,
            product=product,
            address=address,
            total_amount=total_amount,
            weight=selected_weight,
            order_date=timezone.now(),
            quantity=quantity,
        )

        return render(request, "order_success.html",
                      {'amount': total_amount, 'bakery': bakery, 'product_categories': product_categories, })


def get_orders(request):
    bakery = Bakery.objects.filter(active=True).first()
    search_query = request.GET.get('search', '')
    product_categories = ProductCategory.objects.all()
    orders = Orders.objects.filter(user=request.user)

    if search_query:
        orders = orders.filter(
            Q(product__name__icontains=search_query) |
            Q(reference__icontains=search_query)
        )

    return render(request, 'orders.html', {
        'orders': orders,
        'bakery': bakery,
        'search_query': search_query,
        'product_categories': product_categories,
    })


def cancel_order(request, order_id):
    order = get_object_or_404(Orders, id=order_id)
    if order.order_state == 'draft' or order.order_state == 'confirm':
        order.order_state = 'cancel'
        order.save()
    return redirect('orders')
