from django.urls import path
from . import views

urlpatterns = [
    # ========================
    # Static Pages
    # ========================
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),

    # ========================
    # Authentication
    # ========================
    path('signup/', views.signup, name='signup'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),

    # ========================
    # Product Views
    # ========================
    path('products/', views.product_list, name='products'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),

    # ========================
    # Cart Functionality
    # ========================
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.cart_view, name='cart'),  # ✅ Use 'cart' as the view name
    path('remove-from-cart/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),

    # ========================
    # Checkout & Orders
    # ========================
    path('checkout/', views.checkout, name='checkout'),
    path('orders/', views.order_history, name='orders'),
]
