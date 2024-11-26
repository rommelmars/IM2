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

def admin_home(request):
    # Check if the user is authenticated and is a superuser
    if not request.user.is_authenticated or not request.user.is_superuser:
        return redirect('home')  # Redirect to the home page if not authenticated or not a superuser
    
    # Get all users from the database
    users = User.objects.all()
    
    # Pass the users to the template
    return render(request, 'authentication/admin_home.html', {'users': users})

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

        # autentication sa user
        user = authenticate(request, username=username, password=password)

        if user is not None:
            # login sa user
            login(request, user)
            messages.success(request, f"Welcome, {username}! You have successfully logged in.")
            return redirect('dashboard')  # Redirect to profile home
        else:
            messages.error(request, "Invalid username or password.") 
            return redirect('signin')

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
        shoes = Shoe.objects.filter(user=request.user, category_id=category_id)
        selected_category = int(category_id)
    else:
        # Otherwise, show all shoes
        shoes = Shoe.objects.filter(user=request.user)
        selected_category = None

    return render(request, "authentication/inventory.html", {
        'shoes': shoes,
        'categories': categories,
        'selected_category': selected_category,
    })

@login_required
def inventory_list(request):
    shoes = Shoe.objects.filter(user=request.user)   
    return render(request, 'inventory.html', {'shoes': shoes})

@login_required
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
            return redirect('inventory')
    else:
        form = ShoeForm(instance=shoe)
    
    return render(request, 'authentication/update_shoe.html', {'form': form})

@login_required
def delete_shoe(request, shoe_id):
    shoe = get_object_or_404(Shoe, id=shoe_id)
    shoe.delete()
    return redirect('inventory')

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
            sale = form.save(commit=False)
            sale.user = request.user
            try:
                sale.save()
                return redirect('inventory')
            except ValueError as e:
                form.add_error(None, str(e))  # Add any unexpected errors to the form
    return render(request, 'authentication/create_sale.html', {
        'form': form,
        'categories': categories,
    })

@login_required
def sales_report(request):
    # Get filter and sorting options from query parameters
    category_id = request.GET.get('category')  # Selected category ID
    sort_by = request.GET.get('sort', 'date')  # Sorting criteria

    # Fetch sales data
    sales = Sale.objects.filter(user=request.user).order_by('-date')

    # Apply category filter if selected
    if category_id:
        sales = sales.filter(shoe__category_id=category_id)

    # Sort sales based on the selected option
    if sort_by == 'quantity':
        sales = sales.order_by('-quantity_sold')
    elif sort_by == 'total_amount':
        sales = sales.order_by('-total_amount')

    # Group sales by date (convert to PH time)
    grouped_sales = {}
    for sale in sales:
        # Convert to PH time zone using django.utils.timezone.localtime
        sale_date = localtime(sale.date).date()

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
    }
    return render(request, 'authentication/sales_report.html', context)

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

        # Update username, first name, last name, and email
        user.username = request.POST.get("username", user.username)
        user.first_name = request.POST.get("fname", user.first_name)
        user.last_name = request.POST.get("lname", user.last_name)
        user.email = request.POST.get("email", user.email)

        # Handle password change
        password1 = request.POST.get("pass1", "")
        password2 = request.POST.get("pass2", "")

        if password1 or password2:  # If either password field is filled
            if password1 == password2:
                if len(password1) >= 8:  # Optional: Enforce a minimum password length
                    user.set_password(password1)
                    update_session_auth_hash(request, user)  # Keeps the user logged in
                    messages.success(request, "Your password has been updated.")
                else:
                    messages.error(request, "Password must be at least 8 characters long.")
                    return redirect("personal_information")
            else:
                messages.error(request, "Passwords do not match.")
                return redirect("personal_information")

        # Save the updated user object
        user.save()
        messages.success(request, "Your information has been updated successfully.")
        return redirect("personal_information")

    return render(request, "authentication/personal_information.html", {"user": request.user})

@login_required
def dashboard(request):
    user = request.user  # Get the logged-in user
    today = now()  # Get the current datetime
    start_date = today - timedelta(days=6)  # Last 7 days

    # Daily sales for the past 7 days, filtered by user
    daily_sales = (
        Sale.objects.filter(user=user, date__gte=start_date, date__lte=today)
        .annotate(day=TruncDate('date'))
        .values('day')
        .annotate(total_sales=Sum('total_amount'))
        .order_by('day')
    )

    # Prepare data for the chart (convert Decimal to float)
    days = [day['day'].strftime('%Y-%m-%d') for day in daily_sales]
    sales_values = [float(day['total_sales'] or 0) for day in daily_sales]  # Convert Decimal to float

    # Total sales today, filtered by user
    total_sales_today = Sale.objects.filter(user=user, date__date=today.date()).aggregate(
        Sum('total_amount')
    )['total_amount__sum'] or 0
    total_sales_today = float(total_sales_today)  # Convert Decimal to float

    # Sales growth calculation (example: percentage change compared to last week)
    last_week_sales = Sale.objects.filter(
        user=user, date__gte=start_date - timedelta(weeks=1), date__lte=start_date
    ).aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    sales_growth = 0
    if last_week_sales > 0:
        sales_growth = ((total_sales_today - last_week_sales) / last_week_sales) * 100

    # Prepare data for low-stock chart, filtered by user
    low_stock_shoes = Shoe.objects.filter(user=user, stock__lte=10).order_by('stock')[:5]
    low_stock_shoes_names = [shoe.name for shoe in low_stock_shoes]
    low_stock_shoes_stocks = [shoe.stock for shoe in low_stock_shoes]

    # Top-selling shoe, filtered by user
    top_selling_shoe = (
        Sale.objects.filter(user=user)
        .values('shoe__name')
        .annotate(total_sold=Sum('quantity_sold'))
        .order_by('-total_sold')
        .first()
    )

    context = {
        'total_sales_today': total_sales_today,
        'days': json.dumps(days),
        'sales_values': json.dumps(sales_values),
        'low_stock_shoes_names': json.dumps(low_stock_shoes_names),
        'low_stock_shoes_stocks': json.dumps(low_stock_shoes_stocks),
        'top_selling_shoe': top_selling_shoe['shoe__name'] if top_selling_shoe else 'N/A',
        'sales_growth': sales_growth,
    }

    return render(request, 'authentication/dashboard.html', context)


@login_required
def dashboard_api(request):
    today = localtime(now()).date()

    # Total sales today (convert Decimal to float)
    total_sales_today = Sale.objects.filter(date__date=today).aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    total_sales_today = float(total_sales_today)  # Convert Decimal to float

    # Top-selling shoe
    top_selling_shoe = (
        Sale.objects.values('shoe__name')
        .annotate(total_sold=Sum('quantity_sold'))
        .order_by('-total_sold')
        .first()
    )

    # Low stock shoes
    low_stock_shoes = Shoe.objects.filter(stock__lte=10).order_by('stock')
    low_stock_shoes_data = [{'name': shoe.name, 'stock': shoe.stock} for shoe in low_stock_shoes]

    # Sales data for the last 7 days
    last_7_days = Sale.objects.filter(date__gte=now() - timedelta(days=6))
    daily_sales = (
        last_7_days.annotate(date=TruncDate('date'))
        .values('date')
        .annotate(total_sales=Sum('total_amount'))
    )

    days = [entry['date'].strftime('%Y-%m-%d') for entry in daily_sales]
    sales_values = [float(entry['total_sales'] or 0) for entry in daily_sales]  # Convert Decimal to float

    return JsonResponse({
        'total_sales_today': total_sales_today,
        'top_selling_shoe': top_selling_shoe or {},
        'low_stock_shoes': low_stock_shoes_data,
        'days': days,
        'sales_values': sales_values,
        'low_stock_shoes_names': [shoe['name'] for shoe in low_stock_shoes_data],
        'low_stock_shoes_stocks': [shoe['stock'] for shoe in low_stock_shoes_data],
    })
