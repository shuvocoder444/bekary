from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import AccountHead, Transaction, LedgerEntry


@admin.register(AccountHead)
class AccountHeadAdmin(ModelAdmin):
    list_display = ['name', 'head_type', 'is_active', 'created_at']
    search_fields = ['name', 'description']
    list_filter = ['head_type', 'is_active']


@admin.register(Transaction)
class TransactionAdmin(ModelAdmin):
    list_display = ['transaction_id', 'transaction_type', 'account_head', 'title', 'amount', 'payment_method', 'date', 'created_at']
    search_fields = ['transaction_id', 'title', 'notes']
    list_filter = ['transaction_type', 'account_head', 'payment_method', 'date']


@admin.register(LedgerEntry)
class LedgerEntryAdmin(ModelAdmin):
    list_display = ['transaction_date', 'account_head', 'description', 'debit', 'credit', 'running_balance', 'reference_number']
    search_fields = ['description', 'reference_number', 'account_head__name']
    list_filter = ['account_head', 'transaction_date']
