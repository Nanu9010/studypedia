from django.contrib import admin
from .models import Cart, CartItem, Order, OrderItem, Coupon, PurchaseRequest, DownloadLog


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'payment_method', 'total_amount', 'status', 'created_at', 'paid_at')
    list_filter = ('status', 'payment_method')
    search_fields = ('user__username', 'razorpay_order_id', 'razorpay_payment_id')
    readonly_fields = ('created_at', 'paid_at')
    ordering = ('-created_at',)


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'content_type', 'object_id', 'quantity', 'price_at_purchase', 'credits_at_purchase')
    list_filter = ('content_type',)


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'created_at', 'updated_at')
    search_fields = ('user__username',)


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'cart', 'content_type', 'object_id', 'quantity')


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ('code', 'discount_type', 'discount_value', 'valid_from', 'valid_to', 'is_active')
    list_filter = ('discount_type', 'is_active')
    search_fields = ('code',)


@admin.register(PurchaseRequest)
class PurchaseRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'content_type', 'object_id', 'amount_paid', 'credits_used', 'status', 'created_at')
    list_filter = ('status', 'content_type')
    search_fields = ('user__username',)
    ordering = ('-created_at',)


@admin.register(DownloadLog)
class DownloadLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'content_type', 'object_id', 'ip_address', 'downloaded_at')
    list_filter = ('content_type',)
    search_fields = ('user__username', 'ip_address')
    ordering = ('-downloaded_at',)
