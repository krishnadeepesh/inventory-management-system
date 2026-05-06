from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.contrib.auth.forms import AuthenticationForm
from django.db.models import Sum, Count
from django.contrib import messages
from django.http import JsonResponse
from .models import User, Category, Product, PurchaseRequest, FeedbackMessage
from .forms import UserSignupForm, CategoryForm, ProductForm, PurchaseRequestForm, FeedbackMessageForm
from django.db import transaction

@never_cache
def homepage(request):
    # If user is already logged in, redirect to their dashboard
    if request.user.is_authenticated:
        if request.user.role == 'ADMIN':
            return redirect('admin_dashboard')
        elif request.user.role == 'MANAGER':
            return redirect('manager_dashboard')
        else:
            return redirect('user_dashboard')
    return render(request, 'core/homepage.html')

@never_cache
def user_signup(request):
    # If user is already logged in, redirect to their dashboard
    if request.user.is_authenticated:
        if request.user.role == 'ADMIN':
            return redirect('admin_dashboard')
        elif request.user.role == 'MANAGER':
            return redirect('manager_dashboard')
        else:
            return redirect('user_dashboard')
            
    if request.method == 'POST':
        form = UserSignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('user_dashboard')
    else:
        form = UserSignupForm()
    return render(request, 'core/signup.html', {'form': form})

@never_cache
def custom_login(request):
    # If user is already logged in, redirect to their dashboard
    if request.user.is_authenticated:
        if request.user.role == 'ADMIN':
            return redirect('admin_dashboard')
        elif request.user.role == 'MANAGER':
            return redirect('manager_dashboard')
        else:
            return redirect('user_dashboard')
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            if user.role == 'ADMIN':
                return redirect('admin_dashboard')
            elif user.role == 'MANAGER':
                return redirect('manager_dashboard')
            else:
                return redirect('user_dashboard')
        else:
            messages.error(request, "Invalid username or password. Please try again.")
    else:
        form = AuthenticationForm()
    return render(request, 'core/login.html', {'form': form})

def custom_logout(request):
    logout(request)
    return redirect('homepage')

@login_required
@never_cache
def redirect_dashboard(request):
    if request.user.role == 'ADMIN':
        return redirect('admin_dashboard')
    elif request.user.role == 'MANAGER':
        return redirect('manager_dashboard')
    else:
        return redirect('user_dashboard')

# ----- ADMIN VIEWS -----
@login_required
@never_cache
def admin_dashboard(request):
    if request.user.role != 'ADMIN':
        return redirect('redirect_dashboard')
    
    total_sales = PurchaseRequest.objects.filter(status='ACCEPTED').aggregate(total=Sum('quantity'))['total'] or 0
    total_users = User.objects.filter(role='USER').count()
    total_managers = User.objects.filter(role='MANAGER').count()
    
    managers = User.objects.filter(role='MANAGER')
    category_id = request.GET.get('category')
    if category_id:
        products = Product.objects.filter(category_id=category_id, is_active=True)
    else:
        products = Product.objects.filter(is_active=True)
    categories = Category.objects.filter(is_active=True)
    orders = PurchaseRequest.objects.all().order_by('-created_at')
    
    if request.method == 'POST':
        # Removed add manager logic from here
        return redirect('admin_dashboard')
    
    context = {
        'total_sales': total_sales,
        'total_users': total_users,
        'total_managers': total_managers,
        'products': products,
        'categories': categories,
    }
    return render(request, 'core/admin_dashboard.html', context)

@login_required
@never_cache
def admin_transactions(request):
    if request.user.role != 'ADMIN':
        return redirect('redirect_dashboard')
    
    orders = PurchaseRequest.objects.all().order_by('-created_at')
    managers = User.objects.filter(role='MANAGER')
    
    return render(request, 'core/admin_transactions.html', {'orders': orders, 'managers': managers})

@login_required
@never_cache
def admin_add_manager(request):
    if request.user.role != 'ADMIN':
        return redirect('redirect_dashboard')
        
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        if User.objects.filter(username=username).exists():
            messages.error(request, f'Username "{username}" is already taken. Please choose another.')
        elif User.objects.filter(email=email).exists():
            messages.error(request, f'Email "{email}" is already registered. Please use a different email.')
        else:
            User.objects.create_user(username=username, email=email, password=password, role='MANAGER')
            messages.success(request, f'Manager "{username}" added successfully!')
            return redirect('admin_managers')
            
    return render(request, 'core/admin_add_manager.html')

@login_required
@never_cache
def admin_managers(request):
    if request.user.role != 'ADMIN':
        return redirect('redirect_dashboard')
        
    managers = User.objects.filter(role='MANAGER')
    return render(request, 'core/admin_managers.html', {'managers': managers})

@login_required
@never_cache
def delete_manager(request, manager_id):
    if request.user.role != 'ADMIN':
        return redirect('redirect_dashboard')
    manager = get_object_or_404(User, id=manager_id, role='MANAGER')
    manager.delete()
    messages.success(request, 'Manager deleted.')
    return redirect('admin_managers')

# ----- MANAGER VIEWS -----
@login_required
@never_cache
def manager_dashboard(request):
    if request.user.role != 'MANAGER':
        return redirect('redirect_dashboard')
    
    category_id = request.GET.get('category')
    if category_id:
        products = Product.objects.filter(manager=request.user, category_id=category_id, is_active=True)
    else:
        products = Product.objects.filter(manager=request.user, is_active=True)
    all_requests = PurchaseRequest.objects.filter(product__manager=request.user).order_by('-created_at')
    categories = Category.objects.filter(is_active=True)
    
    context = {
        'products': products,
        'all_requests': all_requests,
        'categories': categories,
    }
    return render(request, 'core/manager_dashboard.html', context)

@login_required
@never_cache
def manager_requests(request):
    if request.user.role != 'MANAGER':
        return redirect('redirect_dashboard')
    
    all_requests = PurchaseRequest.objects.filter(product__manager=request.user).order_by('-created_at')
    
    context = {
        'all_requests': all_requests,
    }
    return render(request, 'core/manager_requests.html', context)

@login_required
@never_cache
def add_product(request):
    if request.user.role != 'MANAGER':
        return redirect('redirect_dashboard')
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.manager = request.user
            product.save()
            messages.success(request, 'Product added successfully.')
            return redirect('manager_dashboard')
    else:
        form = ProductForm()
    return render(request, 'core/add_product.html', {'form': form})

@login_required
@never_cache
def add_category(request):
    if request.user.role != 'MANAGER':
        return redirect('redirect_dashboard')
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category added successfully.')
            return redirect('manager_dashboard')
    else:
        form = CategoryForm()
    return render(request, 'core/add_category.html', {'form': form})

@login_required
@never_cache
def edit_product(request, pk):
    if request.user.role != 'MANAGER':
        return redirect('redirect_dashboard')
    product = get_object_or_404(Product, pk=pk, manager=request.user)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product updated successfully.')
            return redirect('manager_dashboard')
    else:
        form = ProductForm(instance=product)
    return render(request, 'core/edit_product.html', {'form': form, 'product': product})

@login_required
@never_cache
def delete_product(request, pk):
    if request.user.role != 'MANAGER':
        return redirect('redirect_dashboard')
    product = get_object_or_404(Product, pk=pk, manager=request.user)
    
    # If there is any request from user about the product then instead of deleting hide it
    if PurchaseRequest.objects.filter(product=product).exists():
        product.is_active = False
        product.save()
        messages.success(request, 'Product hidden because it has associated orders.')
    else:
        product.delete()
        messages.success(request, 'Product deleted successfully.')
    
    return redirect('manager_dashboard')

@login_required
@never_cache
def edit_category(request, pk):
    if request.user.role != 'MANAGER':
        return redirect('redirect_dashboard')
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category updated successfully.')
            return redirect('manager_dashboard')
    else:
        form = CategoryForm(instance=category)
    return render(request, 'core/edit_category.html', {'form': form, 'category': category})

@login_required
@never_cache
def delete_category(request, pk):
    if request.user.role != 'MANAGER':
        return redirect('redirect_dashboard')
    category = get_object_or_404(Category, pk=pk)
    
    # If there is any product in this category that has a request, hide the category
    if PurchaseRequest.objects.filter(product__category=category).exists():
        category.is_active = False
        category.save()
        messages.success(request, 'Category hidden because it has products with associated orders.')
    else:
        category.delete()
        messages.success(request, 'Category deleted successfully.')
        
    return redirect('manager_dashboard')


@login_required
@never_cache
def process_request(request, req_id, action):
    if request.user.role != 'MANAGER':
        return redirect('redirect_dashboard')
    
    purchase_request = get_object_or_404(PurchaseRequest, id=req_id, product__manager=request.user)
    if purchase_request.status == 'PENDING':
        if action == 'accept':
            with transaction.atomic():
                if purchase_request.product.stock >= purchase_request.quantity:
                    purchase_request.product.stock -= purchase_request.quantity
                    purchase_request.product.save()
                    purchase_request.status = 'ACCEPTED'
                    purchase_request.save()
                    messages.success(request, 'Request accepted.')
                else:
                    messages.error(request, 'Not enough stock.')
        elif action == 'reject':
            purchase_request.status = 'REJECTED'
            purchase_request.save()
            messages.info(request, 'Request rejected.')
            
    return redirect('manager_requests')

# ----- USER VIEWS -----
@login_required
@never_cache
def user_dashboard(request):
    if request.user.role != 'USER':
        return redirect('redirect_dashboard')
    
    categories = Category.objects.filter(is_active=True)
    category_id = request.GET.get('category')
    if category_id:
        products = Product.objects.filter(category_id=category_id, is_active=True)
    else:
        products = Product.objects.filter(is_active=True)
        
    context = {
        'categories': categories,
        'products': products,
    }
    return render(request, 'core/user_dashboard.html', context)

@login_required
@never_cache
def user_requests(request):
    if request.user.role != 'USER':
        return redirect('redirect_dashboard')
        
    my_requests = PurchaseRequest.objects.filter(user=request.user).order_by('-created_at')
    
    return render(request, 'core/user_requests.html', {'my_requests': my_requests})

@login_required
@never_cache
def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = PurchaseRequestForm(request.POST)
        if form.is_valid():
            req = form.save(commit=False)
            req.user = request.user
            req.product = product
            req.save()
            messages.success(request, 'Purchase request sent successfully!')
            return redirect('user_dashboard')
    else:
        form = PurchaseRequestForm()
    
    return render(request, 'core/product_detail.html', {'product': product, 'form': form})

@login_required
@never_cache
def feedback(request, receiver_id):
    receiver = get_object_or_404(User, id=receiver_id)
    if request.method == 'POST':
        form = FeedbackMessageForm(request.POST)
        if form.is_valid():
            msg = form.save(commit=False)
            msg.sender = request.user
            msg.receiver = receiver
            msg.save()
            # Stay on the same conversation page instead of redirecting away
            return redirect('feedback', receiver_id=receiver_id)
    else:
        form = FeedbackMessageForm()
        
    messages_list = FeedbackMessage.objects.filter(
        sender__in=[request.user, receiver],
        receiver__in=[request.user, receiver]
    ).order_by('created_at')
    
    return render(request, 'core/feedback.html', {'form': form, 'receiver': receiver, 'messages_list': messages_list})
