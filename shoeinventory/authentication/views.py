from django.shortcuts import redirect, render, HttpResponse, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth import logout
from .models import Shoe, Sale, Category  # Import Category model
from .forms import ShoeForm
from django.contrib.auth.decorators import login_required
from .forms import SaleForm
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.db.models import Sum
from django.db.models.functions import TruncDate
from django.contrib.auth import update_session_auth_hash
from django.db.models import Sum, F
from django.utils.timezone import localtime, now, timezone  # Added timezone import
from django.db.models.functions import TruncMonth
from collections import defaultdict
from datetime import datetime, timedelta
from django.db.models import Sum, F, Count
from decimal import Decimal
import json
from django.http import JsonResponse
from django.db import transaction
from django.db.models import F
from django.contrib.messages import get_messages



# Admin Views

def admin_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('pass1')

        # Authenticate the user
        user = authenticate(request, username=username, password=password)

        if user is not None:
            if user.is_superuser:
                # If the user is a superuser, log them in
                login(request, user)
                return redirect('admin_home')  # Redirect to admin home
            else:
                # If the user is not a superuser, show an error message
                messages.error(request, "You must be a superuser to log in.")
                return redirect('admin_login')
        else:
            # If authentication failed (wrong credentials)
            messages.error(request, "Invalid username or password.")
            return redirect('admin_login')

    return render(request, 'authentication/admin_login.html')

@login_required
def admin_home(request):
    if not request.user.is_authenticated or not request.user.is_superuser:
        return redirect('home')

    # Get all users from the database
    users = User.objects.all()
    categories = Category.objects.all()
    selected_category = request.GET.get('category')

    # Filter shoes by selected category or show all
    shoes = Shoe.objects.all() if not selected_category else Shoe.objects.filter(category_id=selected_category)

    # Get all sales and group them by date
    sales = Sale.objects.select_related('user', 'shoe').order_by('-date')
    grouped_sales = {}
    for sale in sales:
        sale_date = localtime(sale.date).date()
        if sale_date not in grouped_sales:
            grouped_sales[sale_date] = []
        grouped_sales[sale_date].append(sale)

    # Total sales per month
    sales_per_month = (
        Sale.objects.annotate(month=F('date__month'))
        .values('month')
        .annotate(total_sales=Sum('total_amount'))
        .order_by('month')
    )
    # Convert Decimal to float for JSON serialization
    sales_data = [float(sale['total_sales']) if sale['total_sales'] else 0.0 for sale in sales_per_month]
    sales_labels = [sale['month'] for sale in sales_per_month]

    # Top 5 user sellers based on total sales amount
    top_users = (
        Sale.objects.values('user__username')
        .annotate(total_sales=Sum('total_amount'))
        .order_by('-total_sales')[:5]
    )
    top_user_sales_data = [float(user['total_sales']) for user in top_users]
    top_user_labels = [user['user__username'] for user in top_users]

    # Top 5 shoe sellers based on quantity sold
    top_shoes = (
        Sale.objects.values('shoe__name')
        .annotate(total_sold=Sum('quantity_sold'))
        .order_by('-total_sold')[:5]
    )
    top_shoes_data = [float(shoe['total_sold']) for shoe in top_shoes]
    top_shoes_labels = [shoe['shoe__name'] for shoe in top_shoes]

    # Lowest stock items
    lowest_stock = Shoe.objects.order_by('stock')[:5]
    lowest_stock_data = [shoe.stock for shoe in lowest_stock]
    lowest_stock_labels = [shoe.name for shoe in lowest_stock]

    # Pass everything to the template, ensuring chart data is serialized
    return render(request, 'authentication/admin_home.html', {
        'users': users,
        'shoes': shoes,
        'categories': categories,
        'selected_category': int(selected_category) if selected_category else None,
        'grouped_sales': grouped_sales,

        # Dashboard data for charts (passing JSON data)
        'sales_data': json.dumps(sales_data),
        'sales_labels': json.dumps(sales_labels),
        'top_user_sales_data': json.dumps(top_user_sales_data),  # Top user sales data
        'top_user_labels': json.dumps(top_user_labels),  # Top user labels
        'top_shoes_data': json.dumps(top_shoes_data),
        'top_shoes_labels': json.dumps(top_shoes_labels),
        'lowest_stock_data': json.dumps(lowest_stock_data),
        'lowest_stock_labels': json.dumps(lowest_stock_labels),
    })

def admin_logout(request):
    logout(request)  # Log out the user
    return redirect('home')  # Redirect to home page after logout


def home(request):
    return render(request, "authentication/index.html")

def signup(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        fname = request.POST.get('fname')
        lname = request.POST.get('lname')
        email = request.POST.get('email')
        pass1 = request.POST.get('pass1')
        pass2 = request.POST.get('pass2')
        
        # validation sa password
        if pass1 != pass2:
            messages.error(request, "Passwords do not match.")
            return redirect('signup')
        
        # create user 
        myuser = User.objects.create_user(username, email, pass1)
        myuser.first_name = fname
        myuser.last_name = lname
        myuser.save()
        
        messages.success(request, "Account created successfully! Please log in.")
        return redirect('signin')
    
    return render(request, "authentication/signup.html")

def signin(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('pass1')

        # Authenticate the user
        user = authenticate(request, username=username, password=password)

        if user is not None:
            # Log the user in
            login(request, user)
            return redirect('inventory')  # Redirect to the inventory page
        else:
            # Show an error message for invalid credentials
            messages.error(request, "Invalid username or password. Please try again.", extra_tags='signin') 
            return redirect('signin')
    
    # Clear all messages to avoid unrelated ones appearing
    storage = messages.get_messages(request)
    storage.used = True  # Mark all messages as used

    return render(request, "authentication/signin.html")

def signout(request):
    logout(request)
    return redirect('home')

def dashboard(request):
    if not request.user.is_authenticated:
        return redirect('signup')
    return render(request, 'dashboard.html')

@login_required
def inventory(request):
    # Get all categories for the filter dropdown
    categories = Category.objects.all()

    # Get the selected category from GET request
    category_id = request.GET.get('category')

    if category_id:
        # If a category is selected, filter the shoes by that category
        shoes = Shoe.objects.filter(category_id=category_id)
        selected_category = int(category_id)
    else:
        # Otherwise, show all shoes
        shoes = Shoe.objects.all()  # Display shoes from all users
        selected_category = None

    return render(request, "authentication/inventory.html", {
        'shoes': shoes,
        'categories': categories,
        'selected_category': selected_category,
    })

@login_required
def inventory_list(request):
    shoes = Shoe.objects.all()  # Display shoes from all users
    return render(request, 'inventory.html', {'shoes': shoes})

@login_required
def admin_add_shoe(request):
    if request.method == 'POST':
        form = ShoeForm(request.POST, request.FILES)
        if form.is_valid():
            shoe = form.save(commit=False)
            shoe.user = request.user  # Assign the current user to the shoe
            shoe.save()  # Save the shoe to the database
            return redirect('admin_home')  # Redirect to the admin home page after successful add
    else:
        form = ShoeForm()  # Create an empty form if it's a GET request
    
    return render(request, 'authentication/admin_addshoe.html', {'form': form})

@login_required #removed
def add_shoe(request):
    if request.method == 'POST':
        form = ShoeForm(request.POST, request.FILES)
        if form.is_valid():
            shoe = form.save(commit=False)
            shoe.user = request.user  
            shoe.save()  
            return redirect('inventory')
    else:
        form = ShoeForm()
    return render(request, 'authentication/add_shoe.html', {'form': form})

@login_required
def sales(request):
    if not request.user.is_authenticated:
        return redirect('signup')
    return render(request, 'sales.html')

def categories(request):
    if not request.user.is_authenticated:
        return redirect('signup')
    return render(request, 'categories.html')

@login_required
def update_shoe(request, shoe_id):
    shoe = Shoe.objects.get(id=shoe_id)
    if request.method == 'POST':
        form = ShoeForm(request.POST, request.FILES, instance=shoe)  
        if form.is_valid():
            form.save()
            return redirect('admin_home')
    else:
        form = ShoeForm(instance=shoe)
    
    return render(request, 'authentication/update_shoe.html', {'form': form})

@login_required
def delete_shoe(request, shoe_id):
    shoe = get_object_or_404(Shoe, id=shoe_id)
    shoe.delete()
    return redirect('admin_home')

@login_required
def profile_home(request):
    return render(request, 'authentication/profile_home.html')

@login_required
def create_sale(request):
    form = SaleForm(request.POST or None)
    categories = Category.objects.all()  # Fetch all categories

    if request.method == 'POST':
        form = SaleForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():  # Ensures all operations succeed or none are applied
                    sale = form.save(commit=False)
                    sale.user = request.user  # Assign the current logged-in user to the sale

                    # Get the shoe being sold
                    shoe = Shoe.objects.select_for_update().get(id=sale.shoe.id)

                    # Check stock availability
                    if sale.quantity_sold > shoe.stock:  # Fetch actual stock value
                        form.add_error(None, f"Not enough stock available for {shoe.name}.")
                    else:
                        # Deduct stock
                        shoe.stock -= sale.quantity_sold
                        shoe.save(update_fields=['stock'])  # Update only the stock field

                        # Calculate the total amount and save the sale
                        sale.total_amount = sale.quantity_sold * shoe.price
                        sale.save()

                        # Redirect or notify user of successful sale
                        messages.success(request, "Sale recorded successfully!")
                        return redirect('create_sale')  # Redirect to the same page

            except Exception as e:
                form.add_error(None, f"An error occurred: {str(e)}")

    return render(request, 'authentication/create_sale.html', {
        'form': form,
        'categories': categories,
    })

@login_required
def sales_report(request):
    # Check if the user is an admin
    is_admin = request.user.is_superuser

    # Fetch sales data:
    if is_admin:
        # Admin can view all sales
        sales = Sale.objects.all().order_by('-date')
    else:
        # Regular users can only view their own sales
        sales = Sale.objects.filter(user=request.user).order_by('-date')

    # Get filter and sorting options from query parameters
    category_id = request.GET.get('category')  # Selected category ID
    sort_by = request.GET.get('sort', 'date')  # Sorting criteria

    # Apply category filter if selected
    if category_id:
        sales = sales.filter(shoe__category_id=category_id)

    # Sort sales based on the selected option
    if sort_by == 'quantity':
        sales = sales.order_by('-quantity_sold')
    elif sort_by == 'total_amount':
        sales = sales.order_by('-total_amount')

    # Group sales by date
    grouped_sales = {}
    for sale in sales:
        sale_date = localtime(sale.date).date()  # Convert to local timezone
        if sale_date not in grouped_sales:
            grouped_sales[sale_date] = []
        grouped_sales[sale_date].append(sale)

    # Fetch all categories for filtering
    categories = Category.objects.all()

    context = {
        'grouped_sales': grouped_sales,  # Grouped sales by date
        'categories': categories,
        'selected_category': int(category_id) if category_id else None,
        'sort_by': sort_by,
        'is_admin': is_admin,  # Indicate if the user is an admin
    }

    # Pass sales data in a way that user can only see their own sales
    if not is_admin:
        # For regular users, we do not want to expose user info (ID, username) of other users
        for date, sales_list in grouped_sales.items():
            for sale in sales_list:
                # Remove sensitive user information for regular users
                sale.user_id = None
                sale.user = None

    return render(request, 'authentication/sales_report.html' if not is_admin else 'authentication/sales_report_admin.html', context)

@login_required
def search_products(request):
    query = request.GET.get('q', '')
    if query:
        results = Shoe.objects.filter(name__icontains=query).values('name', 'image')
        results_list = []
        for shoe in results:
            if shoe['image']:
                shoe['image'] = shoe['image'].url  
            results_list.append(shoe)
        return JsonResponse(results_list, safe=False)  
    return JsonResponse([], safe=False)

@login_required
def personal_information(request):
    if request.method == "POST":
        user = request.user

        # Update user fields
        user.username = request.POST.get("username", user.username)
        user.first_name = request.POST.get("fname", user.first_name)
        user.last_name = request.POST.get("lname", user.last_name)
        user.email = request.POST.get("email", user.email)

        # Handle password update
        password1 = request.POST.get("pass1", "")
        password2 = request.POST.get("pass2", "")

        if password1 or password2:
            if password1 == password2:
                if len(password1) >= 8:
                    user.set_password(password1)
                    update_session_auth_hash(request, user)
                    messages.success(request, "Your password has been updated.")
                else:
                    messages.error(request, "Password must be at least 8 characters long.")
                    return redirect("personal_information")
            else:
                messages.error(request, "Passwords do not match.")
                return redirect("personal_information")

        # Save updated user data
        user.save()
        messages.success(request, "Your information has been updated successfully.")
        return redirect("inventory")

    # Consume all messages (mark them as read)
    storage = get_messages(request)
    for _ in storage:
        pass

    return render(request, "authentication/personal_information.html", {"user": request.user})


