from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Profile, Car, ClientInquiry, Message, Booking
from .forms import ProfileForm, CarForm, ClientInquiryForm, BookingForm
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
    return render(request, 'blog_sale.html', {'cars': cars})

def blog_hire(request):
    cars = Car.objects.filter(car_type='lease', approved=True, available=True)
    return render(request, 'blog_hire.html', {'cars': cars})

# Registration and Login
def register_profile(request, role):
    if request.method == 'POST':
        user_form = UserCreationForm(request.POST)
        profile_form = ProfileForm(request.POST)
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save(commit=False)
            user.is_active = False
            user.save()
            profile = profile_form.save(commit=False)
            profile.user = user
            profile.save()
            messages.success(request, 'Registration submitted. Await admin approval.')
            return redirect('login')
    else:
        user_form = UserCreationForm()
        profile_form = ProfileForm(initial={'role': role})
    return render(request, 'register.html', {'user_form': user_form, 'profile_form': profile_form, 'role': role})

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
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
    return render(request, 'login.html')

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
    profiles = Profile.objects.all()
    cars = Car.objects.all()
    inquiries = ClientInquiry.objects.all()
    return render(request, 'admin_dashboard.html', {'profiles': profiles, 'cars': cars, 'inquiries': inquiries})

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

