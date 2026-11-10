from django.db import models
from django.utils.text import slugify


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Product Category'
        verbose_name_plural = 'Product Categories'
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Product(models.Model):
    UNIT_CHOICES = (
        ('pcs', 'Pieces (Pcs)'),
        ('kg', 'Kilogram (Kg)'),
        ('box', 'Box'),
        ('pack', 'Pack'),
        ('slice', 'Slice / Portion'),
    )

    name = models.CharField(max_length=200)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    sku = models.CharField(max_length=50, unique=True, help_text='Barcode or unique SKU code')
    cost_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, help_text='Production/Cost price')
    selling_price = models.DecimalField(max_digits=10, decimal_places=2, help_text='Retail selling price')
    stock_quantity = models.IntegerField(default=0, help_text='Available finished stock')
    unit = models.CharField(max_length=20, choices=UNIT_CHOICES, default='pcs')
    shelf_life_days = models.PositiveIntegerField(default=3, help_text='Freshness shelf life in days')
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Bakery Product'
        verbose_name_plural = 'Bakery Products'
        ordering = ['-created_at']

    @property
    def profit_margin(self):
        if self.cost_price and self.cost_price > 0:
            return round(((self.selling_price - self.cost_price) / self.cost_price) * 100, 2)
        return 0.0

    @property
    def is_low_stock(self):
        return self.stock_quantity <= 5

    def __str__(self):
        return f"{self.name} ({self.sku})"
