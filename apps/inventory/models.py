from django.db import models
from django.utils import timezone


class RawMaterial(models.Model):
    UNIT_CHOICES = (
        ('kg', 'Kilogram (Kg)'),
        ('gm', 'Gram (Gm)'),
        ('liter', 'Liter (L)'),
        ('ml', 'Milliliter (Ml)'),
        ('pcs', 'Pieces (Pcs)'),
        ('tray', 'Tray / Carton'),
        ('box', 'Packaging Box'),
    )

    name = models.CharField(max_length=150, unique=True)
    unit = models.CharField(max_length=20, choices=UNIT_CHOICES, default='kg')
    current_stock = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    min_stock_alert = models.DecimalField(max_digits=10, decimal_places=2, default=5.00, help_text='Threshold for low stock alert')
    unit_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, help_text='Average purchase cost per unit')
    supplier_name = models.CharField(max_length=150, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Raw Material'
        verbose_name_plural = 'Raw Materials & Ingredients'
        ordering = ['name']

    @property
    def is_low_stock(self):
        return self.current_stock <= self.min_stock_alert

    @property
    def total_stock_value(self):
        return round(self.current_stock * self.unit_cost, 2)

    def __str__(self):
        return f"{self.name} ({self.current_stock} {self.unit})"


class StockMovement(models.Model):
    MOVEMENT_CHOICES = (
        ('purchase', 'Stock In / Purchase'),
        ('used', 'Used in Baking & Kitchen'),
        ('waste', 'Waste / Damaged / Expired'),
        ('return', 'Return to Supplier'),
    )

    material = models.ForeignKey(RawMaterial, on_delete=models.CASCADE, related_name='movements')
    movement_type = models.CharField(max_length=20, choices=MOVEMENT_CHOICES)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    unit_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    date = models.DateField(default=timezone.now)
    note = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Stock Movement'
        verbose_name_plural = 'Stock Movements'
        ordering = ['-date', '-created_at']

    def save(self, *args, **kwargs):
        if not self.total_cost and self.quantity and self.unit_cost:
            self.total_cost = self.quantity * self.unit_cost
        
        # Update raw material stock balance
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        if is_new:
            if self.movement_type == 'purchase':
                self.material.current_stock += self.quantity
                if self.unit_cost > 0:
                    self.material.unit_cost = self.unit_cost
            elif self.movement_type in ['used', 'waste', 'return']:
                self.material.current_stock = max(0, self.material.current_stock - self.quantity)
            self.material.save()

    def __str__(self):
        return f"{self.get_movement_type_display()} - {self.material.name} ({self.quantity} {self.material.unit})"
