from django import forms
from django.utils import timezone
from .models import Customer, Order, CustomCakeOrder


class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['name', 'customer_type', 'phone', 'email', 'address', 'route_area']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full px-3.5 py-2.5 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white text-sm focus:ring-2 focus:ring-amber-500 outline-none'}),
            'customer_type': forms.Select(attrs={'class': 'w-full px-3.5 py-2.5 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white text-sm focus:ring-2 focus:ring-amber-500 outline-none'}),
            'phone': forms.TextInput(attrs={'class': 'w-full px-3.5 py-2.5 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white text-sm focus:ring-2 focus:ring-amber-500 outline-none'}),
            'email': forms.EmailInput(attrs={'class': 'w-full px-3.5 py-2.5 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white text-sm focus:ring-2 focus:ring-amber-500 outline-none'}),
            'address': forms.Textarea(attrs={'rows': 2, 'class': 'w-full px-3.5 py-2.5 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white text-sm focus:ring-2 focus:ring-amber-500 outline-none'}),
            'route_area': forms.TextInput(attrs={'placeholder': 'e.g. Route A - Dhanmondi, Mirpur-10...', 'class': 'w-full px-3.5 py-2.5 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white text-sm focus:ring-2 focus:ring-amber-500 outline-none'}),
        }


class CustomCakeBookingForm(forms.Form):
    customer_name = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'placeholder': 'Customer Name', 'class': 'w-full px-3.5 py-2.5 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white text-sm focus:ring-2 focus:ring-amber-500 outline-none'}))
    customer_phone = forms.CharField(max_length=20, widget=forms.TextInput(attrs={'placeholder': 'Phone Number', 'class': 'w-full px-3.5 py-2.5 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white text-sm focus:ring-2 focus:ring-amber-500 outline-none'}))
    customer_address = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': 'Delivery Address (optional)', 'class': 'w-full px-3.5 py-2.5 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white text-sm focus:ring-2 focus:ring-amber-500 outline-none'}))
    
    flavor = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'placeholder': 'e.g. Belgian Chocolate, Red Velvet, Vanilla Fondant', 'class': 'w-full px-3.5 py-2.5 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white text-sm focus:ring-2 focus:ring-amber-500 outline-none'}))
    weight_lbs = forms.DecimalField(initial=2.0, max_digits=5, decimal_places=2, widget=forms.NumberInput(attrs={'step': '0.5', 'class': 'w-full px-3.5 py-2.5 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white text-sm focus:ring-2 focus:ring-amber-500 outline-none'}))
    tier_count = forms.IntegerField(initial=1, min_value=1, widget=forms.NumberInput(attrs={'class': 'w-full px-3.5 py-2.5 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white text-sm focus:ring-2 focus:ring-amber-500 outline-none'}))
    cake_message = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': 'e.g. Happy 5th Birthday Liam!', 'class': 'w-full px-3.5 py-2.5 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white text-sm focus:ring-2 focus:ring-amber-500 outline-none'}))
    
    delivery_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date', 'min': timezone.localdate().isoformat(), 'class': 'w-full px-3.5 py-2.5 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white text-sm focus:ring-2 focus:ring-amber-500 outline-none'}))
    delivery_time = forms.TimeField(required=False, widget=forms.TimeInput(attrs={'type': 'time', 'class': 'w-full px-3.5 py-2.5 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white text-sm focus:ring-2 focus:ring-amber-500 outline-none'}))
    
    total_amount = forms.DecimalField(max_digits=10, decimal_places=2, widget=forms.NumberInput(attrs={'step': '0.01', 'class': 'w-full px-3.5 py-2.5 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white text-sm focus:ring-2 focus:ring-amber-500 outline-none'}))
    paid_amount = forms.DecimalField(initial=0.00, max_digits=10, decimal_places=2, widget=forms.NumberInput(attrs={'step': '0.01', 'class': 'w-full px-3.5 py-2.5 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white text-sm focus:ring-2 focus:ring-amber-500 outline-none'}))
    payment_method = forms.ChoiceField(choices=Order.PAYMENT_METHOD_CHOICES, widget=forms.Select(attrs={'class': 'w-full px-3.5 py-2.5 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white text-sm focus:ring-2 focus:ring-amber-500 outline-none'}))
    special_instructions = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows': 2, 'placeholder': 'Color palette, theme, ribbons, packaging notes...', 'class': 'w-full px-3.5 py-2.5 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white text-sm focus:ring-2 focus:ring-amber-500 outline-none'}))
