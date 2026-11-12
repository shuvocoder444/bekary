import json
import random
from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.db.models import Sum, F, Count
from django.utils import timezone

from apps.products.models import Product, Category
from apps.finance.models import AccountHead, Transaction
from .models import Customer, Order, OrderItem, CustomCakeOrder
from .forms import CustomerForm, CustomCakeBookingForm


@login_required(login_url='/login/')
def pos_terminal(request):
    categories = Category.objects.filter(is_active=True).prefetch_related('products')
    products = Product.objects.filter(is_active=True).select_related('category')
    customers = Customer.objects.all().order_by('name')

    context = {
        'categories': categories,
        'products': products,
        'customers': customers,
    }
    return render(request, 'pages/pos_terminal.html', context)


@login_required(login_url='/login/')
@transaction.atomic
def pos_checkout(request):
    if request.method != 'POST':
        return redirect('pos_terminal')

    try:
        cart_data = json.loads(request.POST.get('cart_data', '[]'))
        if not cart_data:
            messages.error(request, 'Cart is empty. Please select products first.')
            return redirect('pos_terminal')

        customer_id = request.POST.get('customer_id')
        payment_method = request.POST.get('payment_method', 'cash')
        discount = Decimal(str(request.POST.get('discount', '0') or '0'))
        tax = Decimal(str(request.POST.get('tax', '0') or '0'))
        paid_amount = Decimal(str(request.POST.get('paid_amount', '0') or '0'))

        customer = None
        if customer_id and customer_id != 'walk-in':
            customer = Customer.objects.filter(id=customer_id).first()

        subtotal = Decimal('0.00')
        order_items = []

        # Validate and prepare items
        for item in cart_data:
            product = Product.objects.select_for_update().get(id=item['id'])
            qty = int(item['qty'])
            price = Decimal(str(product.selling_price))
            total_item = price * qty
            subtotal += total_item
            order_items.append((product, qty, price, total_item))

        total_amount = max(Decimal('0.00'), subtotal - discount + tax)
        if paid_amount == 0 and total_amount > 0:
            paid_amount = total_amount  # default fully paid in cash for walk-in

        order = Order.objects.create(
            order_type='pos',
            customer=customer,
            status='completed',
            payment_method=payment_method,
            subtotal=subtotal,
            discount=discount,
            tax=tax,
            total_amount=total_amount,
            paid_amount=paid_amount,
            due_amount=max(Decimal('0.00'), total_amount - paid_amount),
            created_by=request.user
        )

        for product, qty, price, total_item in order_items:
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=qty,
                unit_price=price,
                total_price=total_item
            )
            # Deduct stock
            product.stock_quantity = max(0, product.stock_quantity - qty)
            product.save()

        # Update customer stats
        if customer:
            customer.total_orders += 1
            customer.total_spent += total_amount
            if order.due_amount > 0:
                customer.running_due += order.due_amount
            customer.save()

        # Automatically record transaction & ledger in Finance
        head, _ = AccountHead.objects.get_or_create(
            name="Counter POS Sales Revenue",
            defaults={'head_type': 'income', 'is_active': True}
        )
        Transaction.objects.create(
            transaction_type='income',
            account_head=head,
            title=f"POS Sale Invoice #{order.order_number}",
            amount=paid_amount,
            payment_method=payment_method if payment_method in ['cash', 'card', 'mobile_banking'] else 'cash',
            date=timezone.now().date(),
            reference_order=order,
            created_by=request.user,
            notes=f"Walk-in POS checkout with {len(order_items)} items."
        )

        messages.success(request, f"Order {order.order_number} completed successfully! Total: ৳{order.total_amount}")
        return redirect('order_receipt', order_number=order.order_number)

    except Exception as e:
        messages.error(request, f"Checkout failed: {str(e)}")
        return redirect('pos_terminal')


@login_required(login_url='/login/')
def order_receipt(request, order_number):
    order = get_object_or_404(Order.objects.prefetch_related('items__product', 'customer'), order_number=order_number)
    return render(request, 'pages/order_receipt.html', {'order': order})


@login_required(login_url='/login/')
def custom_cakes_list(request):
    custom_orders = CustomCakeOrder.objects.select_related('order__customer').all()
    booking_form = CustomCakeBookingForm()

    # Metrics
    today = timezone.localdate()
    pending_deliveries = custom_orders.filter(delivery_date=today, order__status__in=['pending', 'baking', 'ready']).count()
    baking_count = custom_orders.filter(order__status='baking').count()
    completed_month = custom_orders.filter(order__status='completed', delivery_date__month=today.month).count()

    context = {
        'custom_orders': custom_orders,
        'booking_form': booking_form,
        'pending_deliveries': pending_deliveries,
        'baking_count': baking_count,
        'completed_month': completed_month,
    }
    return render(request, 'pages/custom_cakes.html', context)


@login_required(login_url='/login/')
@transaction.atomic
def custom_cake_create(request):
    if request.method == 'POST':
        form = CustomCakeBookingForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data

            # 1. Get or Create Customer
            customer, _ = Customer.objects.get_or_create(
                phone=cd['customer_phone'],
                defaults={
                    'name': cd['customer_name'],
                    'address': cd['customer_address'],
                }
            )

            # 2. Create Base Order
            total = cd['total_amount']
            paid = cd['paid_amount']
            due = max(Decimal('0.00'), total - paid)
            payment_status = 'paid' if due == 0 else ('partial' if paid > 0 else 'unpaid')

            order = Order.objects.create(
                order_type='custom_cake',
                customer=customer,
                status='pending',
                payment_status=payment_status,
                payment_method=cd['payment_method'],
                subtotal=total,
                total_amount=total,
                paid_amount=paid,
                due_amount=due,
                notes=cd['special_instructions'],
                created_by=request.user
            )

            # 3. Create Custom Cake Details
            CustomCakeOrder.objects.create(
                order=order,
                flavor=cd['flavor'],
                weight_lbs=cd['weight_lbs'],
                tier_count=cd['tier_count'],
                cake_message=cd['cake_message'],
                delivery_date=cd['delivery_date'],
                delivery_time=cd['delivery_time'],
                special_instructions=cd['special_instructions']
            )

            # 4. Update Customer Metrics
            customer.total_orders += 1
            customer.total_spent += paid
            if due > 0:
                customer.running_due += due
            customer.save()

            # Record Advance Payment into Finance & Ledger if paid > 0
            if paid > 0:
                head, _ = AccountHead.objects.get_or_create(
                    name="Custom Cake Pre-Orders",
                    defaults={'head_type': 'income', 'is_active': True}
                )
                Transaction.objects.create(
                    transaction_type='income',
                    account_head=head,
                    title=f"Custom Cake Advance: {order.order_number}",
                    amount=paid,
                    payment_method=cd['payment_method'] if cd['payment_method'] in ['cash', 'card', 'mobile_banking'] else 'cash',
                    date=timezone.now().date(),
                    reference_order=order,
                    created_by=request.user,
                    notes=f"Advance deposit for {cd['flavor']} ({cd['weight_lbs']} lbs)."
                )

            messages.success(request, f'Custom Cake Booking "{order.order_number}" created successfully!')
        else:
            messages.error(request, 'Please correct the booking form errors.')
    return redirect('custom_cakes_list')


@login_required(login_url='/login/')
def custom_cake_status_update(request, pk):
    cake = get_object_or_404(CustomCakeOrder, pk=pk)
    new_status = request.POST.get('status')
    if new_status in ['pending', 'baking', 'ready', 'completed', 'cancelled']:
        cake.order.status = new_status
        if new_status == 'completed' and cake.order.due_amount > 0:
            cake.order.paid_amount = cake.order.total_amount
            cake.order.due_amount = Decimal('0.00')
            cake.order.payment_status = 'paid'
        cake.order.save()
        messages.success(request, f"Order status updated to '{cake.order.get_status_display()}'")
    return redirect('custom_cakes_list')


@login_required(login_url='/login/')
def customers_list(request):
    customers = Customer.objects.all().order_by('-total_spent')
    form = CustomerForm()
    return render(request, 'pages/customers_list.html', {
        'customers': customers,
        'form': form,
    })


@login_required(login_url='/login/')
def customer_create(request):
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            cust = form.save()
            messages.success(request, f'Customer "{cust.name}" registered successfully!')
        else:
            messages.error(request, 'Error registering customer.')
    return redirect('customers_list')


# ==========================================
# HAWKER & ROUTE DISTRIBUTION MANAGEMENT
# ==========================================

@login_required(login_url='/login/')
def hawker_distribution_list(request):
    hawkers = Customer.objects.filter(customer_type='hawker').order_by('name')
    products = Product.objects.filter(is_active=True).order_by('name')
    
    # Recent Dispatches
    dispatches = Order.objects.filter(
        order_type='hawker_dispatch'
    ).select_related('customer').prefetch_related('items__product').order_by('-created_at')[:40]

    # Metrics
    today = timezone.localdate()
    today_dispatches = Order.objects.filter(order_type='hawker_dispatch', created_at__date=today)
    today_dispatches_count = today_dispatches.count()
    today_delivered_amount = today_dispatches.aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')
    total_hawker_due = hawkers.aggregate(due=Sum('running_due'))['due'] or Decimal('0.00')

    context = {
        'hawkers': hawkers,
        'products': products,
        'dispatches': dispatches,
        'today_dispatches_count': today_dispatches_count,
        'today_delivered_amount': today_delivered_amount,
        'total_hawker_due': total_hawker_due,
    }
    return render(request, 'pages/hawker_distribution.html', context)


@login_required(login_url='/login/')
@transaction.atomic
def hawker_dispatch_create(request):
    hawkers = Customer.objects.filter(customer_type='hawker').order_by('name')
    products = Product.objects.filter(is_active=True).order_by('name')

    if request.method != 'POST':
        context = {
            'hawkers': hawkers,
            'products': products,
            'today': timezone.localdate(),
        }
        return render(request, 'pages/hawker_dispatch_create.html', context)

    try:
        hawker_id = request.POST.get('hawker_id')
        hawker = get_object_or_404(Customer, id=hawker_id, customer_type='hawker')

        product_ids = request.POST.getlist('product_id[]')
        quantities = request.POST.getlist('quantity[]')
        rates = request.POST.getlist('rate[]')

        paid_amount = Decimal(str(request.POST.get('paid_amount', '0') or '0'))
        payment_method = request.POST.get('payment_method', 'cash')
        notes = request.POST.get('notes', '')

        order_items = []
        subtotal = Decimal('0.00')

        for p_id, qty_str, rate_str in zip(product_ids, quantities, rates):
            if not p_id or not qty_str:
                continue
            qty = int(qty_str)
            if qty <= 0:
                continue

            product = Product.objects.select_for_update().get(id=p_id)
            rate = Decimal(str(rate_str)) if rate_str else Decimal(str(product.selling_price))
            total_item = rate * qty
            subtotal += total_item

            # Deduct finished goods stock
            product.stock_quantity = max(0, product.stock_quantity - qty)
            product.save()

            order_items.append((product, qty, rate, total_item))

        if not order_items:
            messages.error(request, 'No products selected for hawker dispatch.')
            return redirect('hawker_distribution_list')

        total_amount = subtotal
        due_amount = max(Decimal('0.00'), total_amount - paid_amount)
        payment_status = 'paid' if due_amount == 0 else ('partial' if paid_amount > 0 else 'unpaid')

        # Create Order
        order = Order.objects.create(
            order_type='hawker_dispatch',
            customer=hawker,
            status='completed',
            payment_status=payment_status,
            payment_method=payment_method,
            subtotal=subtotal,
            total_amount=total_amount,
            paid_amount=paid_amount,
            due_amount=due_amount,
            notes=notes,
            created_by=request.user
        )

        for product, qty, rate, total_item in order_items:
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=qty,
                unit_price=rate,
                total_price=total_item
            )

        # Update Hawker running stats
        hawker.total_orders += 1
        hawker.total_spent += total_amount
        hawker.running_due += due_amount
        hawker.save()

        # Record Cash Collection into Finance
        if paid_amount > 0:
            head, _ = AccountHead.objects.get_or_create(
                name="Hawker Route Delivery Collections",
                defaults={'head_type': 'income', 'is_active': True}
            )
            Transaction.objects.create(
                transaction_type='income',
                account_head=head,
                title=f"Hawker Dispatch #{order.order_number} ({hawker.name})",
                amount=paid_amount,
                payment_method=payment_method,
                date=timezone.now().date(),
                reference_order=order,
                created_by=request.user,
                notes=f"Cash collected against challan #{order.order_number}. Remaining due: ৳{due_amount}"
            )

        messages.success(request, f"Challan #{order.order_number} generated for {hawker.name}! Due: ৳{due_amount}")
        return redirect('order_receipt', order_number=order.order_number)

    except Exception as e:
        messages.error(request, f"Hawker dispatch failed: {str(e)}")
        return redirect('hawker_distribution_list')


@login_required(login_url='/login/')
def hawker_sales_report(request):
    today = timezone.localdate()
    start_date = request.GET.get('start_date') or today.replace(day=1).isoformat()
    end_date = request.GET.get('end_date') or today.isoformat()
    selected_hawker_id = request.GET.get('hawker_id')

    hawkers = Customer.objects.filter(customer_type='hawker').order_by('name')

    dispatches = Order.objects.filter(
        order_type='hawker_dispatch',
        created_at__date__range=[start_date, end_date]
    ).prefetch_related('items__product', 'customer').order_by('-created_at')

    if selected_hawker_id:
        dispatches = dispatches.filter(customer_id=selected_hawker_id)

    # Aggregated items delivered to hawkers in range
    item_breakdown = OrderItem.objects.filter(
        order__in=dispatches
    ).values(
        'product__name', 'product__unit'
    ).annotate(
        total_quantity=Sum('quantity'),
        total_value=Sum('total_price')
    ).order_by('-total_quantity')

    # Summary totals
    total_sales_value = dispatches.aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')
    total_cash_collected = dispatches.aggregate(paid=Sum('paid_amount'))['paid'] or Decimal('0.00')
    total_due_added = dispatches.aggregate(due=Sum('due_amount'))['due'] or Decimal('0.00')

    context = {
        'hawkers': hawkers,
        'dispatches': dispatches,
        'item_breakdown': item_breakdown,
        'start_date': start_date,
        'end_date': end_date,
        'selected_hawker_id': selected_hawker_id,
        'total_sales_value': total_sales_value,
        'total_cash_collected': total_cash_collected,
        'total_due_added': total_due_added,
    }
    return render(request, 'pages/hawker_reports.html', context)
