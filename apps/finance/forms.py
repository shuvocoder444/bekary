from django import forms
from .models import Transaction, AccountHead


class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['transaction_type', 'account_head', 'title', 'amount', 'payment_method', 'date', 'receipt_voucher', 'notes']
        widgets = {
            'transaction_type': forms.Select(attrs={'class': 'w-full px-3.5 py-2.5 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white text-sm focus:ring-2 focus:ring-amber-500 outline-none'}),
            'account_head': forms.Select(attrs={'class': 'w-full px-3.5 py-2.5 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white text-sm focus:ring-2 focus:ring-amber-500 outline-none'}),
            'title': forms.TextInput(attrs={'placeholder': 'e.g. Monthly Electricity Bill, Packaging Boxes', 'class': 'w-full px-3.5 py-2.5 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white text-sm focus:ring-2 focus:ring-amber-500 outline-none'}),
            'amount': forms.NumberInput(attrs={'step': '0.01', 'placeholder': '0.00', 'class': 'w-full px-3.5 py-2.5 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white text-sm focus:ring-2 focus:ring-amber-500 outline-none'}),
            'payment_method': forms.Select(attrs={'class': 'w-full px-3.5 py-2.5 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white text-sm focus:ring-2 focus:ring-amber-500 outline-none'}),
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'w-full px-3.5 py-2.5 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white text-sm focus:ring-2 focus:ring-amber-500 outline-none'}),
            'receipt_voucher': forms.FileInput(attrs={'class': 'w-full text-sm text-gray-500 dark:text-gray-400 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-amber-50 dark:file:bg-amber-900/40 file:text-amber-700 dark:file:text-amber-300 hover:file:bg-amber-100'}),
            'notes': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Additional remarks or voucher reference...', 'class': 'w-full px-3.5 py-2.5 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white text-sm focus:ring-2 focus:ring-amber-500 outline-none'}),
        }
