from django.contrib import admin
from .models import Product, Cart, CartItem, Order, OrderItem


@admin.action(description='Mark selected orders as shipped')
def mark_as_shipped(modeladmin, request, queryset):
    queryset.update(status='SHIPPED')


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    readonly_fields = ('product', 'quantity')
    extra = 0  # Disable adding extra empty rows


class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'created_at', 'total_price', 'status', 'list_order_items')
    list_filter = ('status',)
    actions = [mark_as_shipped]
    inlines = [OrderItemInline]


admin.site.register(Product)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem)
