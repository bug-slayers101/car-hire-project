from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from .models import Profile, Car, ClientInquiry, Message, Booking
from .forms import ProfileForm, CarForm, ClientInquiryForm, BookingForm, LoginForm, UserRegistrationForm
from django.contrib import messages
from django.utils import timezone
from datetime import date

# Public views
def index(request):
    return render(request, 'index.html')

def about(request):
    return render(request, 'about.html')

def contact(request):
    if request.method == 'POST':
        # Handle contact form
        pass
    return render(request, 'contacts.html')

def blog_sale(request):
    cars = Car.objects.filter(car_type='sale', approved=True, available=True)
    query = request.GET.get('q')
    if query:
        cars = cars.filter(model__icontains=query)
    return render(request, 'blog_sale.html', {'cars': cars})

def blog_hire(request):
    cars = Car.objects.filter(car_type='lease', approved=True, available=True)
    query = request.GET.get('q')
    if query:
        cars = cars.filter(model__icontains=query)
    return render(request, 'blog_hire.html', {'cars': cars})

def car_detail(request, car_id):
    car = get_object_or_404(Car, id=car_id, approved=True)
    return render(request, 'car_detail.html', {'car': car})

# Registration and Login
def register_profile(request, role):
    # Validate role from URL
    if role not in ['owner', 'client']:
        messages.error(request, 'Invalid registration role.')
        return redirect('home')
    
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        profile_form = ProfileForm(request.POST)
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save(commit=False)
            user.is_active = False
            user.save()
            profile = profile_form.save(commit=False)
            profile.user = user
            profile.role = role  # Force role from URL parameter
            profile.save()
            messages.success(request, 'Registration submitted. Await admin approval.')
            return redirect('login')
    else:
        user_form = UserRegistrationForm()
        profile_form = ProfileForm(initial={'role': role})
    return render(request, 'register.html', {'user_form': user_form, 'profile_form': profile_form, 'role': role})

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None and user.is_active:
                try:
                    profile = Profile.objects.get(user=user)
                    login(request, user)
                    if user.is_staff:
                        return redirect('admin_dashboard')
                    elif profile.role == 'owner':
                        return redirect('owner_dashboard')
                    else:
                        return redirect('client_dashboard')
                except Profile.DoesNotExist:
                    messages.error(request, 'Profile not found.')
            else:
                messages.error(request, 'Invalid credentials or account not active.')
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})

# Client views
@login_required
def client_dashboard(request):
    profile = get_object_or_404(Profile, user=request.user, role='client')
    inquiries = ClientInquiry.objects.filter(client=request.user)
    messages_list = Message.objects.filter(user=request.user, read=False)
    return render(request, 'client_dashboard.html', {'inquiries': inquiries, 'messages': messages_list})

@login_required
def inquire_car(request, car_id, inquiry_type):
    car = get_object_or_404(Car, id=car_id)
    if request.method == 'POST':
        form = ClientInquiryForm(request.POST)
        if form.is_valid():
            inquiry = form.save(commit=False)
            inquiry.client = request.user
            inquiry.car = car
            inquiry.inquiry_type = inquiry_type
            if inquiry_type == 'hire':
                # Handle booking form
                booking_form = BookingForm(request.POST)
                if booking_form.is_valid():
                    start_date = booking_form.cleaned_data['start_date']
                    end_date = booking_form.cleaned_data['end_date']
                    # Check availability
                    overlapping = Booking.objects.filter(
                        inquiry__car=car,
                        inquiry__approved=True,
                        start_date__lt=end_date,
                        end_date__gt=start_date
                    ).exists()
                    if overlapping:
                        messages.error(request, 'Car is not available for the selected dates.')
                        return redirect('blog_hire')
                    booking = booking_form.save(commit=False)
                    booking.inquiry = inquiry
                    days = (booking.end_date - booking.start_date).days
                    booking.total_days = days
                    booking.base_price = car.price * days
                    # Calculate overtime if needed (placeholder)
                    booking.total_price = booking.base_price + booking.overtime_charge
                    inquiry.total_price = booking.total_price
                    inquiry.start_date = booking.start_date
                    inquiry.end_date = booking.end_date
                    inquiry.save()
                    booking.save()
            else:
                inquiry.save()
            messages.success(request, 'Inquiry submitted. Await approval.')
            return redirect('client_dashboard')
    else:
        form = ClientInquiryForm()
        booking_form = BookingForm() if inquiry_type == 'hire' else None
    return render(request, 'inquire.html', {'form': form, 'booking_form': booking_form, 'car': car, 'inquiry_type': inquiry_type})

@login_required
def make_payment(request, inquiry_id):
    inquiry = get_object_or_404(ClientInquiry, id=inquiry_id, client=request.user, approved=True)
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'accept':
            # Process payment
            messages.success(request, f'Payment for {inquiry.car.model} processed.')
            return redirect('client_dashboard')
        else:
            inquiry.delete()
            messages.info(request, 'Inquiry cancelled.')
            return redirect('client_dashboard')
    return render(request, 'pay.html', {'inquiry': inquiry})

# Owner views
@login_required
def owner_dashboard(request):
    profile = get_object_or_404(Profile, user=request.user, role='owner')
    cars = Car.objects.filter(owner=request.user)
    messages_list = Message.objects.filter(user=request.user, read=False)
    return render(request, 'owner_dashboard.html', {'cars': cars, 'messages': messages_list})

@login_required
def register_car(request):
    if request.method == 'POST':
        form = CarForm(request.POST, request.FILES)
        if form.is_valid():
            car = form.save(commit=False)
            car.owner = request.user
            car.save()
            messages.success(request, 'Car registered. Await approval.')
            return redirect('owner_dashboard')
    else:
        form = CarForm()
    return render(request, 'register_car.html', {'form': form})

@login_required
def cancel_car(request, car_id):
    car = get_object_or_404(Car, id=car_id, owner=request.user)
    if not ClientInquiry.objects.filter(car=car, approved=True).exists():
        car.delete()
        messages.success(request, 'Car removed.')
    else:
        messages.error(request, 'Cannot cancel car that has active inquiries.')
    return redirect('owner_dashboard')

# Admin views
@login_required
def admin_dashboard(request):
    if not request.user.is_staff:
        return redirect('home')
    
    # Separate profiles by role
    client_profiles = Profile.objects.filter(role='client')
    owner_profiles = Profile.objects.filter(role='owner')
    
    # Get cars and inquiries
    cars = Car.objects.all()
    inquiries = ClientInquiry.objects.all()
    
    context = {
        'client_profiles': client_profiles,
        'owner_profiles': owner_profiles,
        'cars': cars,
        'inquiries': inquiries,
    }
    return render(request, 'admin_dashboard.html', context)

@login_required
def approve_inquiry(request, inquiry_id):
    if not request.user.is_staff:
        return redirect('home')
    inquiry = get_object_or_404(ClientInquiry, id=inquiry_id)
    inquiry.approved = True
    inquiry.save()
    return redirect('admin_dashboard')

@login_required
def revoke_user(request, user_id):
    if not request.user.is_staff:
        return redirect('home')
    user = get_object_or_404(User, id=user_id)
    user.is_active = False
    user.save()
    Message.objects.create(user=user, content='Your account has been revoked by admin.')
    return redirect('admin_dashboard')

def logout_view(request):
    logout(request)
    return redirect('home')

