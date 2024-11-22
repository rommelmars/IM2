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
            return redirect('profile_home')  # Redirect to profile home
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
    if request.method == 'POST':
        form = SaleForm(request.POST)
        if form.is_valid():
            sale = form.save(commit=False)
            sale.user = request.user  
            try:
                sale.save()  
                return redirect('inventory') 
            except ValueError as e:
                form.add_error(None, str(e)) 
    else:
        form = SaleForm()
    return render(request, 'authentication/create_sale.html', {'form': form})

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

    # Group sales by date
    sales_by_date = (
        sales.annotate(sale_date=TruncDate('date'))
        .values('sale_date')
        .annotate(total_quantity=Sum('quantity_sold'), total_amount=Sum('total_amount'))
        .order_by('-sale_date')
    )

    # Fetch all categories for filtering
    categories = Category.objects.all()

    context = {
        'sales': sales,
        'sales_by_date': sales_by_date,
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
