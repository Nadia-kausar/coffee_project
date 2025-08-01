from django.contrib import admin
from .models import Product, Order, OrderItem

# =====================
# Product Admin
# =====================
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'price', 'formatted_price')
    search_fields = ('name',)
    list_filter = ('price',)

    @admin.display(description='Price (PKR)')
    def formatted_price(self, obj):
        return f"PKR {obj.price:.2f}"


# =====================
# Order Admin
# =====================
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'created_at', 'status', 'display_total')
    search_fields = ('user__username',)
    list_filter = ('created_at', 'status', 'user')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)

    @admin.display(description='Total (PKR)')
    def display_total(self, obj):
        return f"PKR {obj.total:.2f}"

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(user=request.user)


# =====================
# OrderItem Admin
# =====================
@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'product', 'quantity', 'item_price', 'get_item_total')
    search_fields = ('order__user__username', 'product__name')
    list_filter = ('order__created_at',)

    @admin.display(description='Item Price (PKR)')
    def item_price(self, obj):
        return f"PKR {obj.product.price:.2f}"

    @admin.display(description='Item Total (PKR)')
    def get_item_total(self, obj):
        return f"PKR {obj.total_price:.2f}"
