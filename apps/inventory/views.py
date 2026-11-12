import json
import random
from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.db.models import Sum, F, Count
from django.utils import timezone

from apps.products.models import Product
from .models import RawMaterial, StockMovement, ProductionBatch, BatchConsumption, BatchOutput
from .forms import RawMaterialForm, StockMovementForm


@login_required(login_url='/login/')
def inventory_list(request):
    materials = RawMaterial.objects.all().order_by('name')
    movements = StockMovement.objects.select_related('material').all()[:20]

    # Calculate metrics
    total_materials = materials.count()
    low_stock_count = sum(1 for m in materials if m.is_low_stock)
    total_value = sum(m.total_stock_value for m in materials)

    material_form = RawMaterialForm()
    movement_form = StockMovementForm()

    context = {
        'materials': materials,
        'movements': movements,
        'total_materials': total_materials,
        'low_stock_count': low_stock_count,
        'total_value': total_value,
        'material_form': material_form,
        'movement_form': movement_form,
    }
    return render(request, 'pages/inventory_list.html', context)


@login_required(login_url='/login/')
def material_create(request):
    if request.method == 'POST':
        form = RawMaterialForm(request.POST)
        if form.is_valid():
            mat = form.save()
            messages.success(request, f'Ingredient "{mat.name}" added to inventory!')
        else:
            messages.error(request, 'Error saving raw material.')
    return redirect('inventory_list')


@login_required(login_url='/login/')
def stock_movement_create(request):
    if request.method == 'POST':
        form = StockMovementForm(request.POST)
        if form.is_valid():
            movement = form.save()
            messages.success(request, f'Stock movement for "{movement.material.name}" recorded!')
        else:
            messages.error(request, 'Error logging stock movement.')
    return redirect('inventory_list')


@login_required(login_url='/login/')
def production_batches_list(request):
    batches = ProductionBatch.objects.prefetch_related('consumptions__material', 'outputs__product').all()
    raw_materials = RawMaterial.objects.all().order_by('name')
    products = Product.objects.filter(is_active=True).order_by('name')

    # Metrics
    today = timezone.localdate()
    today_batches_count = batches.filter(production_date=today).count()
    total_outputs_count = sum(b.total_output_quantity for b in batches)
    total_cost_all = batches.aggregate(total=Sum('total_raw_material_cost'))['total'] or Decimal('0.00')

    context = {
        'batches': batches,
        'raw_materials': raw_materials,
        'products': products,
        'today_batches_count': today_batches_count,
        'total_outputs_count': total_outputs_count,
        'total_cost_all': total_cost_all,
    }
    return render(request, 'pages/production_batches.html', context)


@login_required(login_url='/login/')
@transaction.atomic
def production_batch_create(request):
    raw_materials = RawMaterial.objects.all().order_by('name')
    products = Product.objects.filter(is_active=True).order_by('name')

    if request.method != 'POST':
        context = {
            'raw_materials': raw_materials,
            'products': products,
            'today': timezone.localdate(),
        }
        return render(request, 'pages/production_batch_create.html', context)

    try:
        production_date = request.POST.get('production_date') or timezone.localdate()
        notes = request.POST.get('notes', '')

        # Generate unique batch number
        batch_number = f"BATCH-{timezone.now().strftime('%Y%m%d')}-{random.randint(1000, 9999)}"

        batch = ProductionBatch.objects.create(
            batch_number=batch_number,
            production_date=production_date,
            notes=notes,
            created_by=request.user
        )

        # Process Consumed Raw Materials
        material_ids = request.POST.getlist('material_id[]')
        material_qtys = request.POST.getlist('material_qty[]')

        total_cost = Decimal('0.00')
        consumed_summary = []

        for m_id, m_qty in zip(material_ids, material_qtys):
            if not m_id or not m_qty:
                continue
            qty = Decimal(str(m_qty))
            if qty <= 0:
                continue

            material = RawMaterial.objects.select_for_update().get(id=m_id)
            unit_cost = material.unit_cost
            item_cost = round(qty * unit_cost, 2)
            total_cost += item_cost

            # Record Consumption
            BatchConsumption.objects.create(
                batch=batch,
                material=material,
                quantity=qty,
                unit_cost=unit_cost,
                total_cost=item_cost
            )

            # Record StockMovement (automatically updates material current_stock balance)
            StockMovement.objects.create(
                material=material,
                movement_type='used',
                quantity=qty,
                unit_cost=unit_cost,
                total_cost=item_cost,
                date=production_date,
                note=f"Used in Batch #{batch.batch_number}"
            )
            consumed_summary.append(f"{material.name}: {qty} {material.unit}")

        # Process Finished Products Output
        product_ids = request.POST.getlist('product_id[]')
        product_qtys = request.POST.getlist('product_qty[]')

        total_units = 0
        output_items = []
        for p_id, p_qty in zip(product_ids, product_qtys):
            if not p_id or not p_qty:
                continue
            qty = int(p_qty)
            if qty <= 0:
                continue

            product = Product.objects.select_for_update().get(id=p_id)
            product.stock_quantity += qty
            product.save()

            total_units += qty
            output_items.append((product, qty))

        # Allocate unit cost per product
        unit_cost_allocated = Decimal('0.00')
        if total_units > 0 and total_cost > 0:
            unit_cost_allocated = round(total_cost / Decimal(str(total_units)), 2)

        for product, qty in output_items:
            BatchOutput.objects.create(
                batch=batch,
                product=product,
                quantity=qty,
                unit_cost=unit_cost_allocated
            )

        batch.total_raw_material_cost = total_cost
        batch.save()

        messages.success(request, f"Production Batch {batch.batch_number} created successfully! Stock updated.")
    except Exception as e:
        messages.error(request, f"Production Batch error: {str(e)}")

    return redirect('production_batches_list')


@login_required(login_url='/login/')
def production_reports(request):
    today = timezone.localdate()
    start_date = request.GET.get('start_date') or today.replace(day=1).isoformat()
    end_date = request.GET.get('end_date') or today.isoformat()

    batches = ProductionBatch.objects.filter(
        production_date__range=[start_date, end_date]
    ).prefetch_related('consumptions__material', 'outputs__product').order_by('-production_date')

    # Aggregated Raw Materials consumed in range
    material_usage = BatchConsumption.objects.filter(
        batch__production_date__range=[start_date, end_date]
    ).values(
        'material__name', 'material__unit'
    ).annotate(
        total_quantity=Sum('quantity'),
        total_expense=Sum('total_cost')
    ).order_by('-total_expense')

    # Aggregated Products baked in range
    product_outputs = BatchOutput.objects.filter(
        batch__production_date__range=[start_date, end_date]
    ).values(
        'product__name', 'product__unit'
    ).annotate(
        total_quantity=Sum('quantity')
    ).order_by('-total_quantity')

    # Summary totals
    total_material_cost = sum(m['total_expense'] or Decimal('0.00') for m in material_usage)
    total_pieces_produced = sum(p['total_quantity'] or 0 for p in product_outputs)
    total_batches_count = batches.count()

    context = {
        'batches': batches,
        'material_usage': material_usage,
        'product_outputs': product_outputs,
        'start_date': start_date,
        'end_date': end_date,
        'total_material_cost': total_material_cost,
        'total_pieces_produced': total_pieces_produced,
        'total_batches_count': total_batches_count,
    }
    return render(request, 'pages/production_reports.html', context)
