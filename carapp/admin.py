from django.contrib import admin
from .models import Profile, Car, ClientInquiry, Message, Booking

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'phone_number', 'id_number', 'approved')
    list_editable = ('approved',)
    search_fields = ('user__username', 'id_number')

@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_display = ('model', 'plate', 'price', 'car_type', 'approved', 'available', 'owner')
    list_editable = ('approved', 'available')
    search_fields = ('model', 'plate', 'owner__username')

@admin.register(ClientInquiry)
class ClientInquiryAdmin(admin.ModelAdmin):
    list_display = ('client_name', 'car', 'inquiry_type', 'approved', 'created_at')
    list_editable = ('approved',)
    search_fields = ('client_name', 'client_email', 'car__model')

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('user', 'content', 'date', 'read')
    list_editable = ('read',)
    search_fields = ('user__username', 'content')

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('inquiry', 'start_date', 'end_date', 'total_price')
    search_fields = ('inquiry__client_name', 'inquiry__car__model')

