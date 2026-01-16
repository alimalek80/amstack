from django.contrib import admin
from django.utils.html import format_html

from .models import Order, OrderItem, BasketItem, Invoice


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product_name', 'product_type', 'unit_price', 'quantity', 'total_price')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'user_email', 'status', 'total_amount', 'created_at', 'paid_at')
    list_filter = ('status', 'created_at', 'paid_at')
    search_fields = ('order_number', 'user__email', 'billing_name', 'billing_email')
    readonly_fields = ('order_number', 'created_at', 'updated_at', 'paid_at')
    inlines = [OrderItemInline]
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Order Information', {
            'fields': ('order_number', 'user', 'status', 'created_at', 'updated_at', 'paid_at')
        }),
        ('Billing Information', {
            'fields': ('billing_name', 'billing_email', 'billing_address')
        }),
        ('Financial Details', {
            'fields': ('subtotal', 'tax_amount', 'discount_amount', 'total_amount')
        }),
        ('Payment Details', {
            'fields': ('payment_method', 'payment_transaction_id', 'payment_amount')
        }),
        ('Legacy Fields', {
            'fields': ('product_type', 'post', 'course', 'service', 'amount', 'reference'),
            'classes': ('collapse',)
        }),
    )
    
    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'User Email'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'product_name', 'product_type', 'quantity', 'unit_price', 'total_price')
    list_filter = ('product_type', 'created_at')
    search_fields = ('order__order_number', 'product_name')
    readonly_fields = ('total_price', 'created_at')
    ordering = ('-created_at',)
    
    def order_number(self, obj):
        return obj.order.order_number
    order_number.short_description = 'Order Number'


@admin.register(BasketItem)
class BasketItemAdmin(admin.ModelAdmin):
    list_display = ('user_email', 'product_name', 'quantity', 'unit_price_display', 'total_price_display', 'created_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('user__email',)
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)
    
    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'User Email'
    
    def product_name(self, obj):
        product = obj.get_product()
        return str(product) if product else 'No product'
    product_name.short_description = 'Product'
    
    def unit_price_display(self, obj):
        return f"${obj.get_unit_price()}"
    unit_price_display.short_description = 'Unit Price'
    
    def total_price_display(self, obj):
        return f"${obj.get_total_price()}"
    total_price_display.short_description = 'Total Price'


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('invoice_number', 'order_number', 'amount', 'issue_date')
    list_filter = ('issue_date',)
    search_fields = ('invoice_number', 'order__order_number', 'order__billing_email')
    readonly_fields = ('invoice_number', 'issue_date')
    ordering = ('-issue_date',)
    
    fieldsets = (
        ('Invoice Information', {
            'fields': ('invoice_number', 'order', 'issue_date', 'due_date')
        }),
        ('Financial Details', {
            'fields': ('subtotal', 'tax_amount', 'discount_amount', 'amount')
        }),
        ('File Management', {
            'fields': ('pdf_file',)
        }),
    )
    
    def order_number(self, obj):
        return obj.order.order_number
    order_number.short_description = 'Order Number'
