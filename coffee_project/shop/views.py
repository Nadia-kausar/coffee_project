from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from decimal import Decimal
from .models import Product, Order, OrderItem

# ========================
# Static Pages
# ========================
@login_required(login_url='login')
def home(request):
    products = Product.objects.all()
    testimonials = [
        {"name": "Alice Johnson", "content": "Incredible service and quality!"},
        {"name": "Mark Davis", "content": "Fast delivery and delicious coffee."},
        {"name": "Sarah Lee", "content": "Best online coffee shop experience ever."},
    ]
    return render(request, 'home.html', {'products': products, 'testimonials': testimonials})

def about(request):
    return render(request, 'about.html')

# ========================
# Authentication
# ========================
def signup(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        if not all([username, email, password1, password2]):
            messages.error(request, "Please fill all fields.")
            return redirect('signup')

        if password1 != password2:
            messages.error(request, "Passwords do not match.")
            return redirect('signup')

        if User.objects.filter(username=email).exists():
            messages.error(request, "Email already registered.")
            return redirect('signup')

        user = User.objects.create_user(username=email, email=email, password=password1, first_name=username)
        login(request, user)
        messages.success(request, f"Welcome, {username}! Your account was created.")
        return redirect('home')

    return render(request, 'signup.html')

def user_login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, username=email, password=password)

        if user:
            login(request, user)
            messages.success(request, "Logged in successfully.")
            return redirect('home')
        else:
            messages.error(request, "Invalid email or password.")
            return redirect('login')

    return render(request, 'login.html')

@login_required(login_url='login')
def user_logout(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('login')

# ========================
# Product Views
# ========================
@login_required(login_url='login')
def product_list(request):
    products = Product.objects.all()
    return render(request, 'products.html', {'products': products})

@login_required(login_url='login')
def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    return render(request, 'product_detail.html', {'product': product})

# ========================
# Cart Functionality
# ========================
@login_required(login_url='login')
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    order, _ = Order.objects.get_or_create(user=request.user, status='cart')

    if request.method == 'POST':
        try:
            quantity = int(request.POST.get('quantity', 1))
            if quantity < 1:
                messages.error(request, "Quantity must be at least 1.")
                return redirect('product_detail', product_id=product.id)
        except (ValueError, TypeError):
            messages.error(request, "Invalid quantity.")
            return redirect('product_detail', product_id=product.id)

        item, created = OrderItem.objects.get_or_create(order=order, product=product)
        if not created:
            item.quantity += quantity
        else:
            item.quantity = quantity
        item.save()
        order.calculate_total()
        messages.success(request, f"{product.name} added to cart.")
        return redirect('cart')

    return redirect('products')

@login_required(login_url='login')
def cart_view(request):
    order = Order.objects.filter(user=request.user, status='cart').first()

    if not order or not order.items.exists():
        return render(request, 'cart.html', {
            'order': None,
            'order_items': [],
            'total_price': Decimal('0.00'),
            'tax': Decimal('0.00'),
            'total_with_tax': Decimal('0.00'),
        })

    # Prepare list of dicts with item and total price for each
    order_items_with_totals = []
    for item in order.items.all():
        total_price = item.product.price * item.quantity
        order_items_with_totals.append({
            'item': item,
            'total_price': total_price
        })

    if request.method == 'POST':
        for entry in order_items_with_totals:
            item = entry['item']
            try:
                qty = int(request.POST.get(f'quantity_{item.id}', item.quantity))
                if qty <= 0:
                    item.delete()
                else:
                    item.quantity = qty
                    item.save()
            except ValueError:
                messages.error(request, "Invalid quantity.")
        order.calculate_total()
        messages.success(request, "Cart updated successfully.")
        return redirect('cart')

    tax = order.total * Decimal('0.08')  # 8% tax
    total_with_tax = order.total + tax

    return render(request, 'cart.html', {
        'order': order,
        'order_items': order_items_with_totals,
        'total_price': order.total,
        'tax': tax,
        'total_with_tax': total_with_tax,
    })

@login_required(login_url='login')
def remove_from_cart(request, item_id):
    item = get_object_or_404(OrderItem, id=item_id, order__user=request.user, order__status='cart')
    order = item.order
    item.delete()
    order.calculate_total()
    messages.success(request, "Item removed from cart.")
    return redirect('cart')

# ========================
# Checkout & Orders
# ========================
@login_required(login_url='login')
def checkout(request):
    order = Order.objects.filter(user=request.user, status='cart').first()

    if not order or not order.items.exists():
        messages.warning(request, "Your cart is empty.")
        return redirect('cart')

    if request.method == 'POST':
        order.status = 'placed'
        order.calculate_total()
        order.save()
        messages.success(request, "Order placed successfully!")
        return redirect('order_history')

    return render(request, 'checkout.html', {
        'order': order,
        'order_items': order.items.all(),
        'total_price': order.total,
    })

@login_required(login_url='login')
def order_history(request):
    orders = Order.objects.filter(user=request.user).exclude(status='cart').order_by('-created_at')
    return render(request, 'order_history.html', {'orders': orders})
