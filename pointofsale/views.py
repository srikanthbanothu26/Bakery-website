from django.shortcuts import render, redirect, get_object_or_404
from .models import Order, ProductCategory, Products, OrderItem, Payment
from .forms import PaymentForm
import json
from django.db.models import Sum
from datetime import datetime
from Home.models import Bakery
from django.contrib.auth.decorators import login_required


@login_required(login_url='user_login')
def index(request):
    bakery = Bakery.objects.filter(active=True).first()
    product_categories = ProductCategory.objects.all()
    products = Products.objects.all()

    selected_category_id = request.POST.get('category_id') or request.GET.get('category_id')
    search_query = request.POST.get('search') or request.GET.get('search')

    if selected_category_id:
        products = products.filter(category_id=selected_category_id)

    if search_query:
        products = products.filter(name__icontains=search_query)

    return render(request, 'pos_index.html', {
        'product_categories': product_categories,
        'products': products,
        'search_query': search_query or '',
        'selected_category_id': selected_category_id,
        'bakery': bakery,
    })


@login_required(login_url='user_login')
def create_order(request):
    if request.method == "POST":
        data = json.loads(request.body)
        products = data.get("cart", [])

        if not products:
            return JsonResponse({'error': 'Cart is empty'}, status=400)

        total = data.get("total", 0)

        # Create the Order
        order = Order.objects.create(user=request.user, total_amount=total, created_at=datetime.now())

        # Add Order Items
        for item in products:
            try:
                product = Products.objects.get(id=item["id"])
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=item["qty"],
                    price=item["price"]
                )
            except Products.DoesNotExist:
                continue  # or handle missing product differently

        return redirect('payment_view', order_id=order.id)


@login_required(login_url='user_login')
def payment_view(request, order_id):
    bakery = Bakery.objects.filter(active=True).first()
    order = get_object_or_404(Order, id=order_id)

    if request.method == "POST":
        form = PaymentForm(request.POST)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.order = order
            if payment.paid:
                payment.paid_at = datetime.now()
            payment.save()
            return redirect('pos_view')
    else:
        form = PaymentForm()

    return render(request, 'payment_form.html', {'form': form, 'order': order, 'bakery': bakery})


@login_required(login_url='user_login')
def view_orders(request):
    bakery = Bakery.objects.filter(active=True).first()
    orders = Order.objects.filter(user=request.user).order_by('-id')

    search_query = request.GET.get('search')
    if search_query:
        orders = orders.filter(reference__icontains=search_query)

    from_datetime = request.GET.get('from_datetime')
    to_datetime = request.GET.get('to_datetime')

    if from_datetime:
        try:
            from_dt = datetime.strptime(from_datetime, "%Y-%m-%dT%H:%M")
            orders = orders.filter(created_at__gte=from_dt)
        except ValueError:
            pass

    if to_datetime:
        try:
            to_dt = datetime.strptime(to_datetime, "%Y-%m-%dT%H:%M")
            orders = orders.filter(created_at__lte=to_dt)
        except ValueError:
            pass

    sum_of_total = orders.aggregate(Sum('total_amount'))['total_amount__sum']

    return render(request, 'pos_orders.html', {
        'orders': orders,
        'sum_of_total': sum_of_total,
        'bakery': bakery,
        'search_query': search_query,
    })


@login_required(login_url='user_login')
def view_order_items(request, order_id):
    bakery = Bakery.objects.filter(active=True).first()
    order = Order.objects.get(id=order_id)
    order_items = OrderItem.objects.filter(order=order)

    search_query = request.POST.get('search') or request.GET.get('search')
    if search_query:
        order_items = order_items.filter(product__name__icontains=search_query)

    sum_of_total = order_items.aggregate(Sum('price'))['price__sum']
    return render(request, 'pos_order_items.html', {
        'order_items': order_items,
        'sum_of_total': sum_of_total,
        'bakery': bakery,
        'order': order,
        'search_query': search_query
    })
