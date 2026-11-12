from decimal import Decimal
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils import timezone
from django.db.models import Sum

from config.htmx_utils import htmx_redirect
from apps.products.models import Product
from apps.inventory.models import RawMaterial
from apps.orders.models import Order, CustomCakeOrder
from apps.finance.models import Transaction
from apps.payroll.models import Employee


def home_view(request):
    featured_products = Product.objects.filter(is_active=True).select_related('category')[:8]
    return render(request, 'landing/index.html', {
        'featured_products': featured_products,
    })


from .forms import RegistrationForm


def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.role = 'sr'  # default staff role
            user.save()
            login(request, user)
            messages.success(request, "Account created successfully! Welcome to BakeMaster Bakery.")
            if getattr(request, 'htmx', False):
                return htmx_redirect(reverse('dashboard'))
            return redirect('dashboard')
        else:
            if getattr(request, 'htmx', False):
                return render(request, 'accounts/partials/register_form.html', {'form': form})
            return render(request, 'accounts/register.html', {'form': form})

    form = RegistrationForm()
    return render(request, 'accounts/register.html', {'form': form})


def custom_login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, "Welcome back! You have logged in successfully.")
            if getattr(request, 'htmx', False):
                return htmx_redirect(reverse('dashboard'))
            return redirect('dashboard')
        else:
            error_msg = "Invalid credentials. Please verify your email/phone and password."
            if getattr(request, 'htmx', False):
                return render(request, 'accounts/partials/login_form.html', {'error': error_msg, 'username': username})
            return render(request, 'accounts/login.html', {'error': error_msg, 'username': username})

    return render(request, 'accounts/login.html')


@login_required(login_url='/login/')
def dashboard_view(request):
    today = timezone.now().date()

    # Sales metrics
    today_orders = Order.objects.filter(created_at__date=today)
    today_sales = today_orders.aggregate(Sum('total_amount'))['total_amount__sum'] or Decimal('0.00')
    today_orders_count = today_orders.count()

    # Finance metrics
    today_income = Transaction.objects.filter(date=today, transaction_type='income').aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
    today_expenses = Transaction.objects.filter(date=today, transaction_type='expense').aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
    today_net_profit = today_income - today_expenses

    # Overall finance
    total_revenue = Transaction.objects.filter(transaction_type='income').aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
    total_expenses = Transaction.objects.filter(transaction_type='expense').aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')

    # Operational metrics
    active_products_count = Product.objects.filter(is_active=True).count()
    low_stock_materials = [m for m in RawMaterial.objects.all() if m.is_low_stock]
    pending_cakes = CustomCakeOrder.objects.filter(order__status__in=['pending', 'baking']).select_related('order', 'order__customer').order_by('delivery_date')[:5]
    recent_orders = Order.objects.select_related('customer').all().order_by('-created_at')[:8]
    recent_transactions = Transaction.objects.select_related('account_head').all().order_by('-date', '-created_at')[:6]

    context = {
        'today_sales': today_sales,
        'today_orders_count': today_orders_count,
        'today_income': today_income,
        'today_expenses': today_expenses,
        'today_net_profit': today_net_profit,
        'total_revenue': total_revenue,
        'total_expenses': total_expenses,
        'active_products_count': active_products_count,
        'low_stock_count': len(low_stock_materials),
        'low_stock_materials': low_stock_materials[:5],
        'pending_cakes': pending_cakes,
        'recent_orders': recent_orders,
        'recent_transactions': recent_transactions,
    }
    return render(request, 'pages/dashboard.html', context)


@login_required(login_url='/login/')
def calendar_view(request):
    cakes = CustomCakeOrder.objects.select_related('order', 'order__customer').all()
    return render(request, 'pages/calendar.html', {'cakes': cakes})


@login_required(login_url='/login/')
def profile_view(request):
    return render(request, 'pages/profile.html')


@login_required(login_url='/login/')
def task_view(request):
    return render(request, 'pages/task.html')


@login_required(login_url='/login/')
def forms_view(request):
    return render(request, 'pages/forms.html')


@login_required(login_url='/login/')
def tables_view(request):
    return render(request, 'pages/tables.html')


@login_required(login_url='/login/')
def pages_view(request):
    return render(request, 'pages/pages.html')


@login_required(login_url='/login/')
def charts_view(request):
    return render(request, 'pages/charts.html')


@login_required(login_url='/login/')
def ui_elements_view(request):
    return render(request, 'pages/ui_elements.html')


def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    if getattr(request, 'htmx', False):
        from config.htmx_utils import htmx_redirect
        return htmx_redirect(reverse('login'))
    return redirect('login')


def switch_language_view(request):
    """
    Switches active language between English ('en') and Bangla ('bn').
    Stores preference in both session and persistent cookie, then redirects back.
    """
    lang = request.GET.get('lang') or request.POST.get('lang') or 'en'
    if lang not in ['en', 'bn']:
        lang = 'en'

    request.session['django_language'] = lang
    next_url = request.GET.get('next') or request.POST.get('next') or request.META.get('HTTP_REFERER') or '/'

    if getattr(request, 'htmx', False):
        from config.htmx_utils import htmx_redirect
        response = htmx_redirect(next_url)
    else:
        response = redirect(next_url)

    # Set cookie for 1 year so choice is remembered across browser sessions
    response.set_cookie('django_language', lang, max_age=365*24*60*60, samesite='Lax')
    return response

