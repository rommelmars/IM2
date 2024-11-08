from django.shortcuts import redirect, render, HttpResponse,get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth import logout
from .models import Shoe, Sale
from .forms import ShoeForm
from django.contrib.auth.decorators import login_required
from .forms import SaleForm
from django.core.exceptions import ValidationError
from django.http import JsonResponse

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
    shoes = Shoe.objects.filter(user=request.user)   
    return render(request, "authentication/inventory.html", {'shoes': shoes})

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
    sales = Sale.objects.filter(user=request.user).order_by('-date')  
    return render(request, 'authentication/sales_report.html', {'sales': sales})

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