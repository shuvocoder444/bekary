import uuid
from django.db import models
from django.conf import settings
from django.utils import timezone
from apps.products.models import Product


class Customer(models.Model):
    name = models.CharField(max_length=150)
    phone = models.CharField(max_length=20, unique=True, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    total_orders = models.PositiveIntegerField(default=0)
    total_spent = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Customer'
        verbose_name_plural = 'Customers'
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.phone or 'No phone'})"


class Order(models.Model):
    ORDER_TYPE_CHOICES = (
        ('pos', 'Counter POS Sale'),
        ('custom_cake', 'Custom Cake Pre-Order'),
        ('delivery', 'Home Delivery'),
    )

    STATUS_CHOICES = (
        ('pending', 'Pending / Booked'),
        ('baking', 'In Baking & Decorating'),
        ('ready', 'Ready for Pickup / Delivery'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )

    PAYMENT_STATUS_CHOICES = (
        ('paid', 'Paid'),
        ('partial', 'Partial / Advance Paid'),
        ('unpaid', 'Unpaid / Due'),
    )

    PAYMENT_METHOD_CHOICES = (
        ('cash', 'Cash'),
        ('card', 'Credit / Debit Card'),
        ('mobile_banking', 'Mobile Banking (bKash/Nagad/Rocket)'),
        ('bank_transfer', 'Bank Transfer'),
    )

    order_number = models.CharField(max_length=50, unique=True, editable=False)
    order_type = models.CharField(max_length=20, choices=ORDER_TYPE_CHOICES, default='pos')
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='completed')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='paid')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default='cash')
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    tax = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    due_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    notes = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Bakery Order'
        verbose_name_plural = 'Bakery Orders & POS'
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.order_number:
            prefix = "POS" if self.order_type == 'pos' else ("CAKE" if self.order_type == 'custom_cake' else "ORD")
            date_str = timezone.now().strftime("%Y%m%d")
            random_suffix = uuid.uuid4().hex[:5].upper()
            self.order_number = f"{prefix}-{date_str}-{random_suffix}"
            
        self.due_amount = max(0, self.total_amount - self.paid_amount)
        if self.paid_amount >= self.total_amount:
            self.payment_status = 'paid'
        elif self.paid_amount > 0:
            self.payment_status = 'partial'
        else:
            self.payment_status = 'unpaid'
            
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.order_number} - {self.get_order_type_display()} ({self.total_amount})"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = 'Order Item'
        verbose_name_plural = 'Order Items'

    def save(self, *args, **kwargs):
        self.total_price = self.quantity * self.unit_price
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"


class CustomCakeOrder(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='cake_detail')
    flavor = models.CharField(max_length=100, help_text='e.g. Belgian Chocolate, Red Velvet, Vanilla Fondant')
    weight_lbs = models.DecimalField(max_digits=5, decimal_places=2, default=2.0, help_text='Weight in pounds (lbs)')
    cake_message = models.CharField(max_length=255, blank=True, null=True, help_text='Message written on top of cake')
    delivery_date = models.DateField()
    delivery_time = models.TimeField(blank=True, null=True)
    tier_count = models.PositiveIntegerField(default=1, help_text='Layers / Tiers')
    reference_image = models.ImageField(upload_to='cake_references/', blank=True, null=True)
    special_instructions = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = 'Custom Cake Detail'
        verbose_name_plural = 'Custom Cake Details'

    def __str__(self):
        return f"Cake Detail for {self.order.order_number} ({self.flavor}, {self.weight_lbs} lbs)"
