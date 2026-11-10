from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import RawMaterial, StockMovement
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
            messages.success(request, f'Stock movement logged for "{movement.material.name}"!')
        else:
            messages.error(request, 'Error logging stock movement.')
    return redirect('inventory_list')
