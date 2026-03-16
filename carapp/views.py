from django.shortcuts import render, get_object_or_404
from .forms import RegisterForm
from django.shortcuts import redirect
from django.contrib.auth import authenticate, login
from .forms import RegisterForm
from django.contrib.auth.models import User 
from .models import Contact
from django.contrib import messages


# Create your views here.
def index(request):
    return render(request, 'index.html')

def about(request):
    return render(request, 'about.html')

def contacts(request):
    if request.method == "POST":
        name = request.POST.get('Name')
        phone_number = request.POST.get('Phone Number')
        email = request.POST.get('Email')
        car_model = request.POST.get('Car Model')
        price = request.POST.get('Price')
        message = request.POST.get('Massage')

        Contact.objects.create(
            name=name,
            phone_number=phone_number,
            email=email,
            car_model=car_model,
            price=price,
            message=message)
    return render(request, 'contacts.html')

def blog(request):
    
    return render(request, 'blog.html')



def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:        
        form = RegisterForm()  
    return render(request, 'register.html', {'form': form})

def login(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('blog')
        else:
            return render(request, 'login.html', {'error': 'Invalid username or password'})
    return render(request, 'login.html')

def make_payment(request):
    cars = get_object_or_404(Car, pk=id)
    form = CarForm(request.POST or None, instance=cars)
    if form.is_valid():
        form.save()
        return redirect('blog')
    return render(request, 'pay.html', {'form': form, 'cars': cars})



def carsdata(request):
    cars = Contact.objects.all()   # fetch all records from database

    context = {
        'cars': cars
    }

    return render(request, 'carsdata.html', context)

def clientdetail(request):
    approved_cars = Contact.objects.filter(approved=True)

    context = {
        'cars': approved_cars
    }

    return render(request, 'clientdetail.html', context)
def register(request):
    register = RegisterForm()      
    return render(request, 'register.html', {'form': register}),

