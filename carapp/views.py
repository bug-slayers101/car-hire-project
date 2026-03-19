from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from .models import Contact, ClientProfile
from .forms import ClientRegistrationForm, ContactForm
from django.contrib import messages


# Create your views here.
def index(request):
    return render(request, 'index.html')

def about(request):
    return render(request, 'about.html')


def blog(request):
    cars = Contact.objects.all()
    return render(request, 'blog.html', {'contacts': cars})


def contact(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        car_model = request.POST.get('car_model')
        price = request.POST.get('price')
        image = request.FILES.get('image')

        Contact.objects.create(
            name=name,
            phone_number=phone,
            email=email,
            car_model=car_model,
            price=price,
            image=image,
        )

        messages.success(request, 'Your contact information has been submitted successfully!')
    return render(request, 'contacts.html')


def register(request):
    if request.method == 'POST':
        form = ClientRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(
                request,
                "Registration submitted. Your account will be activated after admin approval.",
            )
            return redirect('login')
    else:
        form = ClientRegistrationForm()
    return render(request, 'client_registration.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            if not user.is_active:
                return render(request, 'login.html', {'error': 'Your account is not active yet. Please wait for admin approval.'})
            login(request, user)
            if user.is_staff:
                return redirect('carsdata')
            return redirect('clientdashboard')
        return render(request, 'login.html', {'error': 'Invalid username or password'})
    return render(request, 'login.html')


@login_required
def client_dashboard(request):
    # Dashboard for logged-in clients (only core pages accessible)
    return render(request, 'clientdashboard.html')


@login_required
def car_edit(request, id):
    if not request.user.is_staff:
        return redirect('home')
    car = get_object_or_404(Contact, pk=id)
    if request.method == 'POST':
        form = ContactForm(request.POST, request.FILES, instance=car)
        if form.is_valid():
            form.save()
            messages.success(request, 'Car updated successfully.')
            return redirect('carsdata')
    else:
        form = ContactForm(instance=car)
    return render(request, 'car_form.html', {'form': form, 'title': 'Edit Car'})


@login_required
def car_delete(request, id):
    if not request.user.is_staff:
        return redirect('home')
    car = get_object_or_404(Contact, pk=id)
    if request.method == 'POST':
        car.delete()
        messages.success(request, 'Car deleted successfully.')
        return redirect('carsdata')
    return render(request, 'car_confirm_delete.html', {'car': car})

def logout_view(request):
    logout(request)
    return redirect('home')

@login_required
def make_payment(request, id):
    car = get_object_or_404(Contact, pk=id)

    if request.method == 'POST':
        # TODO: Integrate with a real payment gateway.
        messages.success(request, f"Payment submitted for {car.car_model} (ksh {car.price})")
        return redirect('blog')

    return render(request, 'pay.html', {'car': car})



@login_required
def carsdata(request):
    # Only staff members may see and edit car submissions
    if not request.user.is_staff:
        return redirect('home')

    cars = Contact.objects.all()   # fetch all records from database
    return render(request, 'carsdata.html', {'cars': cars})


@login_required
def clientdetail(request):
    # Only staff members may access approved car listing page
    if not request.user.is_staff:
        return redirect('home')

    approved_cars = Contact.objects.filter(approved=True)
    return render(request, 'clientdetail.html', {'cars': approved_cars})

def car_detail(request, id):
    car = get_object_or_404(Contact, pk=id)
    return render(request, 'car_detail.html', {'car': car})

