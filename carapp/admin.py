from django.contrib import admin
from .models import Contact, ClientProfile


# Register your models here.
@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('car_model', 'price', 'approved')
    list_editable = ('approved',)


@admin.register(ClientProfile)
class ClientProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number', 'approved', 'created_at')
    list_editable = ('approved',)
    search_fields = ('user__username', 'user__email')

