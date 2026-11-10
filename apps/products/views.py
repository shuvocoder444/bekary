from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Product, Category
from .forms import ProductForm


@login_required(login_url='/login/')
def products_list(request):
    category_id = request.GET.get('category')
    search_query = request.GET.get('search', '').strip()

    products = Product.objects.select_related('category').all()

    if category_id:
        products = products.filter(category_id=category_id)
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) | Q(sku__icontains=search_query)
        )

    categories = Category.objects.filter(is_active=True)
    form = ProductForm()

    context = {
        'products': products,
        'categories': categories,
        'selected_category': category_id,
        'search_query': search_query,
        'form': form,
        'total_count': products.count(),
    }
    return render(request, 'pages/products_list.html', context)


@login_required(login_url='/login/')
def product_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save()
            messages.success(request, f'Product "{product.name}" created successfully!')
            return redirect('products_list')
        else:
            messages.error(request, 'Please check the form for errors.')
    else:
        form = ProductForm()

    products = Product.objects.select_related('category').all()
    categories = Category.objects.filter(is_active=True)
    return render(request, 'pages/products_list.html', {
        'products': products,
        'categories': categories,
        'form': form,
    })


@login_required(login_url='/login/')
def product_edit(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, f'Product "{product.name}" updated successfully!')
            return redirect('products_list')
        else:
            messages.error(request, 'Error updating product. Please verify fields.')
    else:
        form = ProductForm(instance=product)

    return render(request, 'pages/product_form_modal.html', {
        'form': form,
        'product': product,
    })


@login_required(login_url='/login/')
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        name = product.name
        product.delete()
        messages.success(request, f'Product "{name}" deleted successfully.')
    return redirect('products_list')
