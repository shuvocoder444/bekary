from django import forms
from .models import Transaction, AccountHead


INPUT_CLASS = 'w-full px-3.5 py-2.5 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white text-sm focus:ring-2 focus:ring-amber-500 outline-none'


class AccountHeadForm(forms.ModelForm):
    class Meta:
        model = AccountHead
        fields = ['name', 'head_type', 'description', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={
                'placeholder': 'e.g. Cake Sales, Flour & Sugar, Electricity Bill',
                'class': INPUT_CLASS,
            }),
            'head_type': forms.Select(attrs={'class': INPUT_CLASS}),
            'description': forms.Textarea(attrs={
                'rows': 2,
                'placeholder': 'Optional description for this category...',
                'class': INPUT_CLASS,
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'h-4 w-4 rounded border-gray-300 text-amber-600 focus:ring-amber-500 dark:border-gray-600 dark:bg-gray-800',
            }),
        }

    def clean_name(self):
        name = (self.cleaned_data.get('name') or '').strip()
        if not name:
            raise forms.ValidationError('Category name is required.')
        qs = AccountHead.objects.filter(name__iexact=name)
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError(f'A category named "{name}" already exists.')
        return name


class TransactionForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['account_head'].queryset = AccountHead.objects.filter(is_active=True).order_by('head_type', 'name')

    class Meta:
        model = Transaction
        fields = ['transaction_type', 'account_head', 'title', 'amount', 'payment_method', 'date', 'receipt_voucher', 'notes']
        widgets = {
            'transaction_type': forms.Select(attrs={'class': INPUT_CLASS}),
            'account_head': forms.Select(attrs={'class': INPUT_CLASS}),
            'title': forms.TextInput(attrs={'placeholder': 'e.g. Monthly Electricity Bill, Packaging Boxes', 'class': INPUT_CLASS}),
            'amount': forms.NumberInput(attrs={'step': '0.01', 'placeholder': '0.00', 'class': INPUT_CLASS}),
            'payment_method': forms.Select(attrs={'class': INPUT_CLASS}),
            'date': forms.DateInput(attrs={'type': 'date', 'class': INPUT_CLASS}),
            'receipt_voucher': forms.FileInput(attrs={'class': 'w-full text-sm text-gray-500 dark:text-gray-400 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-amber-50 dark:file:bg-amber-900/40 file:text-amber-700 dark:file:text-amber-300 hover:file:bg-amber-100'}),
            'notes': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Additional remarks or voucher reference...', 'class': INPUT_CLASS}),
        }
