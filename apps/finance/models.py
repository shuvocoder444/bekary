import uuid
from django.db import models
from django.conf import settings
from django.utils import timezone


class AccountHead(models.Model):
    TYPE_CHOICES = (
        ('income', 'Income / Revenue'),
        ('expense', 'Expense / Cost'),
        ('asset', 'Asset (Cash / Bank)'),
        ('liability', 'Liability / Due'),
    )

    name = models.CharField(max_length=150, unique=True)
    head_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Account Head'
        verbose_name_plural = 'Account Heads'
        ordering = ['head_type', 'name']

    def __str__(self):
        return f"{self.name} ({self.get_head_type_display()})"


class Transaction(models.Model):
    TYPE_CHOICES = (
        ('income', 'Income (+ Inflow)'),
        ('expense', 'Expense (- Outflow)'),
    )

    PAYMENT_METHOD_CHOICES = (
        ('cash', 'Cash in Drawer'),
        ('bank', 'Bank Account Transfer'),
        ('mobile_banking', 'Mobile Banking (bKash/Nagad)'),
        ('card', 'POS Card Machine'),
    )

    transaction_id = models.CharField(max_length=50, unique=True, editable=False)
    transaction_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    account_head = models.ForeignKey(AccountHead, on_delete=models.CASCADE, related_name='transactions')
    title = models.CharField(max_length=200)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default='cash')
    date = models.DateField(default=timezone.now)
    reference_order = models.ForeignKey('orders.Order', on_delete=models.SET_NULL, null=True, blank=True, related_name='financial_transactions')
    reference_payroll = models.ForeignKey('payroll.SalaryPayment', on_delete=models.SET_NULL, null=True, blank=True, related_name='financial_transactions')
    receipt_voucher = models.FileField(upload_to='receipts/', blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Financial Transaction'
        verbose_name_plural = 'Income & Expenses'
        ordering = ['-date', '-created_at']

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        if not self.transaction_id:
            prefix = "INC" if self.transaction_type == 'income' else "EXP"
            date_str = timezone.now().strftime("%Y%m%d")
            random_suffix = uuid.uuid4().hex[:5].upper()
            self.transaction_id = f"{prefix}-{date_str}-{random_suffix}"
        super().save(*args, **kwargs)

        if is_new:
            # Automatically record double-entry in General Ledger
            debit = self.amount if self.transaction_type == 'expense' else 0
            credit = self.amount if self.transaction_type == 'income' else 0
            
            # Fetch latest ledger balance
            last_entry = LedgerEntry.objects.order_by('-id').first()
            current_balance = last_entry.running_balance if last_entry else 0
            new_balance = current_balance + credit - debit

            LedgerEntry.objects.create(
                transaction_date=self.date,
                account_head=self.account_head,
                description=f"{self.title} ({self.get_payment_method_display()})",
                debit=debit,
                credit=credit,
                running_balance=new_balance,
                reference_number=self.transaction_id
            )

    def __str__(self):
        return f"{self.transaction_id} - {self.title} ({self.amount})"


class LedgerEntry(models.Model):
    transaction_date = models.DateField(default=timezone.now)
    account_head = models.ForeignKey(AccountHead, on_delete=models.CASCADE, related_name='ledger_entries')
    description = models.CharField(max_length=255)
    debit = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, help_text='Expense / Cash Out')
    credit = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, help_text='Income / Cash In')
    running_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    reference_number = models.CharField(max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'General Ledger Entry'
        verbose_name_plural = 'General Ledger'
        ordering = ['-transaction_date', '-id']

    def __str__(self):
        return f"{self.transaction_date} | {self.account_head.name} | Dr: {self.debit} | Cr: {self.credit} | Bal: {self.running_balance}"
