from django.conf import settings
from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.db.models import Q
from decimal import Decimal
import uuid


class Order(models.Model):
    """Represents a paid order for courses, blog posts, or services."""

    STATUS_PENDING = 'pending'
    STATUS_PAID = 'paid'
    STATUS_FAILED = 'failed'
    STATUS_REFUNDED = 'refunded'
    STATUS_CANCELLED = 'cancelled'
    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_PAID, 'Paid'),
        (STATUS_FAILED, 'Failed'),
        (STATUS_REFUNDED, 'Refunded'),
        (STATUS_CANCELLED, 'Cancelled'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='orders'
    )
    order_number = models.CharField(max_length=20, unique=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING
    )
    
    # Billing information
    billing_name = models.CharField(max_length=255, blank=True)
    billing_email = models.EmailField(blank=True)
    billing_address = models.TextField(blank=True)
    
    # Financial details
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Payment details
    payment_method = models.CharField(max_length=50, blank=True)
    payment_transaction_id = models.CharField(max_length=255, blank=True)
    payment_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    
    # Legacy fields for backward compatibility
    product_type = models.CharField(max_length=20, blank=True)
    post = models.ForeignKey(
        'blog.Post',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='orders'
    )
    course = models.ForeignKey(
        'courses.Course',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='orders'
    )
    service = models.ForeignKey(
        'services.Service',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='orders'
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # Legacy field
    reference = models.CharField(max_length=40, blank=True)  # Legacy field

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['status']),
            models.Index(fields=['order_number']),
        ]

    def __str__(self):
        return f"Order {self.order_number or self.id} - {self.billing_name}"

    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = self.generate_order_number()
        if not self.billing_name and self.user:
            self.billing_name = self.user.get_full_name() or self.user.email
        if not self.billing_email and self.user:
            self.billing_email = self.user.email
        super().save(*args, **kwargs)

    def generate_order_number(self):
        """Generate a unique order number."""
        import datetime
        timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        random_part = uuid.uuid4().hex[:4].upper()
        return f"ORD-{timestamp}-{random_part}"

    def mark_paid(self, payment_method='demo', transaction_id='', payment_amount=None):
        """Mark the order as paid and create invoice."""
        if self.status == self.STATUS_PAID:
            return
        
        self.status = self.STATUS_PAID
        self.paid_at = timezone.now()
        self.payment_method = payment_method
        self.payment_transaction_id = transaction_id or uuid.uuid4().hex
        self.payment_amount = payment_amount or self.total_amount
        self.save(update_fields=['status', 'paid_at', 'payment_method', 'payment_transaction_id', 'payment_amount', 'updated_at'])
        
        # Create invoice
        Invoice.objects.get_or_create(
            order=self,
            defaults={
                'amount': self.total_amount,
                'tax_amount': self.tax_amount,
                'subtotal': self.subtotal,
            }
        )

    def calculate_totals(self):
        """Calculate order totals from order items."""
        items = self.items.all()
        self.subtotal = sum(item.total_price for item in items)
        # Simple tax calculation (can be enhanced)
        self.tax_amount = Decimal('0.00')  # No tax for now
        self.total_amount = self.subtotal - self.discount_amount + self.tax_amount
        self.save(update_fields=['subtotal', 'tax_amount', 'total_amount', 'updated_at'])

    def grant_access_to_products(self):
        """Grant access to purchased products."""
        from courses.models import CourseEnrollment
        
        for item in self.items.all():
            if item.course:
                CourseEnrollment.objects.get_or_create(
                    user=self.user,
                    course=item.course
                )

    # Legacy methods for backward compatibility
    def get_product(self):
        # For legacy orders
        if self.post:
            return self.post
        if self.course:
            return self.course
        if self.service:
            return self.service
        # For new orders, get first item's product
        first_item = self.items.first()
        return first_item.get_product() if first_item else None

    def get_product_label(self):
        product = self.get_product()
        if product:
            return str(product)
        # For orders with multiple items
        item_count = self.items.count()
        if item_count > 1:
            return f"{item_count} items"
        elif item_count == 1:
            return str(self.items.first().get_product())
        return 'Unknown product'

    def get_product_type_for_target(self):
        if self.post_id:
            return 'post'
        if self.course_id:
            return 'course'
        if self.service_id:
            return 'service'

class OrderItem(models.Model):
    """Individual items within an order with price snapshots."""
    
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items'
    )
    
    # Product relations (only one should be set per item)
    post = models.ForeignKey(
        'blog.Post',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='order_items'
    )
    course = models.ForeignKey(
        'courses.Course',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='order_items'
    )
    service = models.ForeignKey(
        'services.Service',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='order_items'
    )
    
    # Price snapshot at time of purchase
    product_name = models.CharField(max_length=255)
    product_type = models.CharField(max_length=20)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.product_name} (x{self.quantity}) - ${self.total_price}"
    
    def save(self, *args, **kwargs):
        if not self.product_name:
            product = self.get_product()
            self.product_name = str(product) if product else 'Unknown Product'
        
        if not self.product_type:
            if self.post:
                self.product_type = 'post'
            elif self.course:
                self.product_type = 'course'
            elif self.service:
                self.product_type = 'service'
        
        self.total_price = self.unit_price * self.quantity
        super().save(*args, **kwargs)
    
    def get_product(self):
        if self.post:
            return self.post
        if self.course:
            return self.course
        if self.service:
            return self.service
        return None


class Invoice(models.Model):
    """Invoice for completed orders."""
    
    order = models.OneToOneField(
        Order,
        on_delete=models.CASCADE,
        related_name='invoice'
    )
    invoice_number = models.CharField(max_length=20, unique=True, blank=True)
    
    # Financial details (snapshot)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Invoice details
    issue_date = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField(null=True, blank=True)
    
    # PDF generation
    pdf_file = models.FileField(upload_to='invoices/', blank=True, null=True)
    
    class Meta:
        ordering = ['-issue_date']
        indexes = [
            models.Index(fields=['invoice_number']),
            models.Index(fields=['-issue_date']),
        ]
    
    def __str__(self):
        return f"Invoice {self.invoice_number} - ${self.amount}"
    
    def save(self, *args, **kwargs):
        if not self.invoice_number:
            self.invoice_number = self.generate_invoice_number()
        super().save(*args, **kwargs)
    
    def generate_invoice_number(self):
        """Generate a unique invoice number."""
        import datetime
        timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        random_part = uuid.uuid4().hex[:4].upper()
        return f"INV-{timestamp}-{random_part}"
    
    def generate_pdf(self):
        """Generate PDF invoice (placeholder for now)."""
        # This would generate a PDF file
        # For now, we'll just mark it as generated
        pass


class BasketItem(models.Model):
    """Represents an item in a user's shopping basket/cart."""
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='basket_items'
    )
    
    # Product relations (only one should be set per item)
    post = models.ForeignKey(
        'blog.Post',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='basket_items'
    )
    course = models.ForeignKey(
        'courses.Course',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='basket_items'
    )
    service = models.ForeignKey(
        'services.Service',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='basket_items'
    )
    
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'post'],
                condition=Q(post__isnull=False),
                name='unique_post_basket_per_user',
            ),
            models.UniqueConstraint(
                fields=['user', 'course'],
                condition=Q(course__isnull=False),
                name='unique_course_basket_per_user',
            ),
            models.UniqueConstraint(
                fields=['user', 'service'],
                condition=Q(service__isnull=False),
                name='unique_service_basket_per_user',
            ),
        ]
    
    def __str__(self):
        product = self.get_product()
        return f"{product} (x{self.quantity}) - {self.user.email}"
    
    def clean(self):
        targets = [self.post, self.course, self.service]
        if sum(1 for target in targets if target) != 1:
            raise ValidationError('Exactly one target (post, course, or service) must be set for a basket item.')
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
    
    def get_product(self):
        """Get the associated product (post, course, or service)."""
        if self.post:
            return self.post
        if self.course:
            return self.course
        if self.service:
            return self.service
        return None
    
    def get_product_type(self):
        """Get the product type as string."""
        if self.post:
            return 'post'
        if self.course:
            return 'course'
        if self.service:
            return 'service'
        return None
    
    def get_unit_price(self):
        """Get the unit price of the product."""
        product = self.get_product()
        if not product:
            return Decimal('0.00')
        
        if hasattr(product, 'price') and product.price:
            return Decimal(str(product.price))
        if hasattr(product, 'fixed_price') and product.fixed_price:
            return Decimal(str(product.fixed_price))
        if hasattr(product, 'starting_price') and product.starting_price:
            return Decimal(str(product.starting_price))
        
        return Decimal('0.00')
    
    def get_price(self):
        """Alias for get_unit_price for backward compatibility."""
        return self.get_unit_price()
    
    def get_total_price(self):
        """Get the total price (unit price × quantity)."""
        return self.get_unit_price() * self.quantity
    """Items in a user's shopping basket."""
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='basket_items'
    )
    
    # Product relations (only one should be set per item)
    post = models.ForeignKey(
        'blog.Post',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='basket_items'
    )
    course = models.ForeignKey(
        'courses.Course',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='basket_items'
    )
    service = models.ForeignKey(
        'services.Service',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='basket_items'
    )
    
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-added_at']
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'post'],
                condition=Q(post__isnull=False),
                name='unique_post_basket_item_per_user',
            ),
            models.UniqueConstraint(
                fields=['user', 'course'],
                condition=Q(course__isnull=False),
                name='unique_course_basket_item_per_user',
            ),
            models.UniqueConstraint(
                fields=['user', 'service'],
                condition=Q(service__isnull=False),
                name='unique_service_basket_item_per_user',
            ),
        ]
    
    def __str__(self):
        product = self.get_product()
        return f"{self.user.email}'s basket: {product} (x{self.quantity})"
    
    def clean(self):
        targets = [self.post, self.course, self.service]
        if sum(1 for target in targets if target) != 1:
            raise ValidationError('Exactly one target (post, course, or service) must be set for a basket item.')
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
    
    def get_product(self):
        if self.post:
            return self.post
        if self.course:
            return self.course
        if self.service:
            return self.service
        return None
    
    def get_product_type(self):
        if self.post:
            return Order.PRODUCT_POST
        if self.course:
            return Order.PRODUCT_COURSE
        if self.service:
            return Order.PRODUCT_SERVICE
        return None
    
    def get_unit_price(self):
        if self.post:
            return Decimal(self.post.price or 0)
        if self.course:
            return Decimal(self.course.price or 0)
        if self.service:
            return Decimal(self.service.fixed_price or self.service.starting_price or 0)
        return Decimal('0.00')
    
    def get_total_price(self):
        return self.get_unit_price() * self.quantity