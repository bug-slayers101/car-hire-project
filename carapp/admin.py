from django.contrib import admin
from .models import Profile, Car, ClientInquiry, Message, Booking, MpesaTransaction

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('get_user_info', 'role', 'phone_number', 'id_number', 'approved')
    search_fields = ('user__username', 'id_number')

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')

    def get_user_info(self, obj):
        try:
            return obj.user.username
        except:
            return f"User {obj.user_id}"

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

@admin.register(MpesaTransaction)
class MpesaTransactionAdmin(admin.ModelAdmin):
    list_display = ('inquiry', 'amount', 'phone_number', 'status', 'transaction_id', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('inquiry__client_name', 'transaction_id', 'phone_number')

