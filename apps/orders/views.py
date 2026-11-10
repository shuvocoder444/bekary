import json
from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db import transaction
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
    order = get_object_or_404(Order.objects.prefetch_related('items__product'), order_number=order_number)
    return render(request, 'pages/order_receipt.html', {'order': order})


@login_required(login_url='/login/')
def custom_cakes_list(request):
    status_filter = request.GET.get('status')
    cakes = CustomCakeOrder.objects.select_related('order', 'order__customer').all().order_by('-delivery_date')

    if status_filter:
        cakes = cakes.filter(order__status=status_filter)

    booking_form = CustomCakeBookingForm()

    counts = {
        'all': CustomCakeOrder.objects.count(),
        'pending': CustomCakeOrder.objects.filter(order__status='pending').count(),
        'baking': CustomCakeOrder.objects.filter(order__status='baking').count(),
        'ready': CustomCakeOrder.objects.filter(order__status='ready').count(),
        'completed': CustomCakeOrder.objects.filter(order__status='completed').count(),
    }

    context = {
        'cakes': cakes,
        'selected_status': status_filter,
        'counts': counts,
        'booking_form': booking_form,
    }
    return render(request, 'pages/custom_cakes_list.html', context)


@login_required(login_url='/login/')
def custom_cake_create(request):
    if request.method == 'POST':
        form = CustomCakeBookingForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            
            # Find or create customer
            customer, _ = Customer.objects.get_or_create(
                phone=cd['customer_phone'],
                defaults={
                    'name': cd['customer_name'],
                    'address': cd.get('customer_address', ''),
                }
            )

            total = cd['total_amount']
            paid = cd['paid_amount']

            order = Order.objects.create(
                order_type='custom_cake',
                customer=customer,
                status='pending',
                payment_method=cd['payment_method'],
                subtotal=total,
                total_amount=total,
                paid_amount=paid,
                due_amount=max(Decimal('0.00'), total - paid),
                created_by=request.user,
                notes=cd.get('special_instructions', '')
            )

            CustomCakeOrder.objects.create(
                order=order,
                flavor=cd['flavor'],
                weight_lbs=cd['weight_lbs'],
                tier_count=cd['tier_count'],
                cake_message=cd.get('cake_message', ''),
                delivery_date=cd['delivery_date'],
                delivery_time=cd.get('delivery_time'),
                special_instructions=cd.get('special_instructions', '')
            )

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
            # Settle due payment if marked completed
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
