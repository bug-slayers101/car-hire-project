from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from .models import Profile, Car, ClientInquiry, Message, Booking, MpesaTransaction
from .forms import ProfileForm, CarForm, ClientInquiryForm, BookingForm, LoginForm, UserRegistrationForm
from .mpesa_utils import MpesaAPI
from django.contrib import messages
from django.utils import timezone
from datetime import date
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

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
    if request.user.is_authenticated:
        if request.user.is_superuser:
            return redirect('admin_dashboard')
        profile = Profile.objects.filter(user=request.user).first()
        if profile and profile.role == 'owner':
            return redirect('owner_dashboard')
        if profile and profile.role == 'client':
            return redirect('client_dashboard')
        return redirect('home')

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None and user.is_active:
                login(request, user)
                if user.is_superuser:
                    return redirect('admin_dashboard')

                profile = Profile.objects.filter(user=user).first()
                if profile is None:
                    logout(request)
                    form.add_error(None, 'Your account is missing a profile. Please contact the administrator.')
                elif profile.role == 'owner':
                    return redirect('owner_dashboard')
                else:
                    return redirect('client_dashboard')
            else:
                form.add_error(None, 'Invalid username or password, or your account is not active yet.')
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
    booking_form = BookingForm(request.POST or None) if inquiry_type == 'hire' else None
    if request.method == 'POST':
        form = ClientInquiryForm(request.POST)
        if form.is_valid():
            inquiry = form.save(commit=False)
            inquiry.client = request.user
            inquiry.car = car
            inquiry.inquiry_type = inquiry_type
            if inquiry_type == 'hire':
                if booking_form.is_valid():
                    start_date = booking_form.cleaned_data['start_date']
                    end_date = booking_form.cleaned_data['end_date']
                    overlapping = Booking.objects.filter(
                        inquiry__car=car,
                        inquiry__approved=True,
                        start_date__lt=end_date,
                        end_date__gt=start_date
                    ).exists()
                    if overlapping:
                        booking_form.add_error(
                            None,
                            'This car has already been booked for the selected dates. Please choose different dates.'
                        )
                        return render(
                            request,
                            'inquire.html',
                            {'form': form, 'booking_form': booking_form, 'car': car, 'inquiry_type': inquiry_type}
                        )
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
                inquiry.total_price = car.price
                inquiry.save()
            messages.success(request, 'Inquiry submitted. Await approval.')
            return redirect('client_dashboard')
    else:
        form = ClientInquiryForm()
    return render(request, 'inquire.html', {'form': form, 'booking_form': booking_form, 'car': car, 'inquiry_type': inquiry_type})

@login_required
def make_payment(request, inquiry_id):
    inquiry = get_object_or_404(ClientInquiry, id=inquiry_id, client=request.user, approved=True)
    payable_amount = inquiry.total_price if inquiry.total_price is not None else inquiry.car.price

    if payable_amount is None:
        messages.error(request, 'This inquiry does not have a payable amount yet.')
        return redirect('client_dashboard')

    if inquiry.total_price is None:
        inquiry.total_price = payable_amount
        inquiry.save(update_fields=['total_price'])

    if request.method == 'POST':
        phone_number = request.POST.get('phone_number')
        if not phone_number:
            messages.error(request, 'Please provide a phone number.')
            return redirect('make_payment', inquiry_id=inquiry_id)

        # Format phone number to international format
        if phone_number.startswith('0'):
            phone_number = '254' + phone_number[1:]
        elif phone_number.startswith('+'):
            phone_number = phone_number[1:]

        # Initiate M-Pesa STK push
        amount = int(payable_amount)
        account_reference = f"CarHire-{inquiry.id}"
        transaction_desc = f"Payment for {inquiry.car.model}"

        stk_response = MpesaAPI.stk_push(phone_number, amount, account_reference, transaction_desc)

        if 'error' in stk_response:
            messages.error(request, f'Payment initiation failed: {stk_response["error"]}')
            return redirect('make_payment', inquiry_id=inquiry_id)

        # Create M-Pesa transaction record
        transaction = MpesaTransaction.objects.create(
            inquiry=inquiry,
            merchant_request_id=stk_response.get('MerchantRequestID'),
            checkout_request_id=stk_response.get('CheckoutRequestID'),
            amount=amount,
            phone_number=phone_number,
            status='pending'
        )

        messages.success(request, 'Payment request sent to your phone. Please complete the payment.')
        return redirect('client_dashboard')

    return render(request, 'pay.html', {'inquiry': inquiry, 'payable_amount': payable_amount})

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
    if not request.user.is_superuser:
        messages.error(request, 'Only superusers can access the admin dashboard.')
        return redirect('home')

    client_profiles = Profile.objects.filter(role='client').select_related('user').order_by('approved', '-created_at')
    owner_profiles = Profile.objects.filter(role='owner').select_related('user').order_by('approved', '-created_at')
    cars = Car.objects.select_related('owner').order_by('approved', '-created_at')
    inquiries = ClientInquiry.objects.select_related('client', 'car', 'car__owner').order_by('approved', '-created_at')
    bookings = Booking.objects.select_related('inquiry', 'inquiry__car', 'inquiry__client').order_by('-start_date', '-end_date')
    mpesa_transactions = MpesaTransaction.objects.select_related('inquiry', 'inquiry__car', 'inquiry__client').order_by('-created_at')
    messages_list = Message.objects.select_related('user').order_by('-date')

    context = {
        'client_profiles': client_profiles,
        'owner_profiles': owner_profiles,
        'cars': cars,
        'inquiries': inquiries,
        'bookings': bookings,
        'mpesa_transactions': mpesa_transactions,
        'messages_list': messages_list,
    }
    return render(request, 'admin_dashboard.html', context)

@login_required
def approve_profile(request, profile_id):
    if request.method != 'POST':
        return redirect('admin_dashboard')
    if not request.user.is_superuser:
        messages.error(request, 'Only superusers can approve profiles.')
        return redirect('home')

    profile = get_object_or_404(Profile.objects.select_related('user'), id=profile_id)
    if profile.approved:
        messages.info(request, f'{profile.user.username} is already approved.')
        return redirect('admin_dashboard')

    profile.approved = True
    profile.save()
    messages.success(request, f'{profile.user.username} has been approved.')
    return redirect('admin_dashboard')


@login_required
def approve_car(request, car_id):
    if request.method != 'POST':
        return redirect('admin_dashboard')
    if not request.user.is_superuser:
        messages.error(request, 'Only superusers can approve cars.')
        return redirect('home')

    car = get_object_or_404(Car.objects.select_related('owner'), id=car_id)
    owner_profile = Profile.objects.filter(user=car.owner, role='owner').first()
    if owner_profile and not owner_profile.approved:
        messages.error(request, f'Approve {car.owner.username} first before approving {car.model}.')
        return redirect('admin_dashboard')

    if car.approved:
        messages.info(request, f'{car.model} is already approved.')
        return redirect('admin_dashboard')

    car.approved = True
    car.save()
    messages.success(request, f'{car.model} ({car.plate}) has been approved.')
    return redirect('admin_dashboard')


@login_required
def approve_inquiry(request, inquiry_id):
    if request.method != 'POST':
        return redirect('admin_dashboard')
    if not request.user.is_superuser:
        messages.error(request, 'Only superusers can approve inquiries.')
        return redirect('home')

    inquiry = get_object_or_404(ClientInquiry.objects.select_related('car', 'client'), id=inquiry_id)
    if not inquiry.car.approved:
        messages.error(request, f'Approve {inquiry.car.model} before approving this inquiry.')
        return redirect('admin_dashboard')
    if inquiry.inquiry_type == 'buy' and not inquiry.car.available:
        messages.error(request, f'{inquiry.car.model} is no longer available for purchase.')
        return redirect('admin_dashboard')
    if inquiry.approved:
        messages.info(request, f'Inquiry from {inquiry.client_name} is already approved.')
        return redirect('admin_dashboard')

    inquiry.approved = True
    inquiry.save()
    messages.success(request, f'Inquiry from {inquiry.client_name} has been approved.')
    return redirect('admin_dashboard')

@login_required
def revoke_user(request, user_id):
    if request.method != 'POST':
        return redirect('admin_dashboard')
    if not request.user.is_superuser:
        messages.error(request, 'Only superusers can revoke users.')
        return redirect('home')
    user = get_object_or_404(User, id=user_id)
    user.is_active = False
    user.save()
    Profile.objects.filter(user=user).update(approved=False)
    Message.objects.create(user=user, content='Your account has been revoked by admin.')
    messages.success(request, f'{user.username} has been revoked.')
    return redirect('admin_dashboard')

def logout_view(request):
    logout(request)
    return redirect('home')

@csrf_exempt
def mpesa_callback(request):
    """Handle M-Pesa payment callback"""
    if request.method == 'POST':
        try:
            callback_data = json.loads(request.body.decode('utf-8'))

            # Extract callback data
            merchant_request_id = callback_data['Body']['stkCallback']['MerchantRequestID']
            checkout_request_id = callback_data['Body']['stkCallback']['CheckoutRequestID']
            result_code = callback_data['Body']['stkCallback']['ResultCode']
            result_desc = callback_data['Body']['stkCallback']['ResultDesc']

            # Find the transaction
            try:
                transaction = MpesaTransaction.objects.get(
                    merchant_request_id=merchant_request_id,
                    checkout_request_id=checkout_request_id
                )
            except MpesaTransaction.DoesNotExist:
                return JsonResponse({'ResultCode': 1, 'ResultDesc': 'Transaction not found'})

            # Update transaction status
            transaction.result_code = result_code
            transaction.result_desc = result_desc

            if result_code == 0:
                # Payment successful
                transaction.status = 'completed'
                callback_metadata = callback_data['Body']['stkCallback']['CallbackMetadata']['Item']

                # Extract transaction details
                for item in callback_metadata:
                    if item['Name'] == 'MpesaReceiptNumber':
                        transaction.transaction_id = item['Value']
                    elif item['Name'] == 'TransactionDate':
                        pass  # Could store transaction date if needed
                    elif item['Name'] == 'PhoneNumber':
                        pass  # Phone number already stored

                transaction.callback_metadata = callback_metadata

                # Mark inquiry as paid and create success message
                inquiry = transaction.inquiry
                # You might want to add a payment status to the inquiry model
                Message.objects.create(
                    user=inquiry.client,
                    content=f'Payment of KSH {transaction.amount} for {inquiry.car.model} was successful. Transaction ID: {transaction.transaction_id}'
                )

            else:
                # Payment failed
                transaction.status = 'failed'
                Message.objects.create(
                    user=transaction.inquiry.client,
                    content=f'Payment for {transaction.inquiry.car.model} failed: {result_desc}'
                )

            transaction.save()

            return JsonResponse({'ResultCode': 0, 'ResultDesc': 'Callback received successfully'})

        except json.JSONDecodeError:
            return JsonResponse({'ResultCode': 1, 'ResultDesc': 'Invalid JSON data'})
        except KeyError as e:
            return JsonResponse({'ResultCode': 1, 'ResultDesc': f'Missing key: {str(e)}'})
        except Exception as e:
            return JsonResponse({'ResultCode': 1, 'ResultDesc': f'Error: {str(e)}'})

    return JsonResponse({'ResultCode': 1, 'ResultDesc': 'Invalid request method'})

