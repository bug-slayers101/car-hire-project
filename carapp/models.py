from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=[('owner', 'Car Owner'), ('client', 'Client')])
    phone_number = models.CharField(max_length=20)
    id_number = models.CharField(max_length=10, unique=True)
    approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.role}"

class Car(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cars')
    model = models.CharField(max_length=100)
    plate = models.CharField(max_length=20, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)  # per day for lease, total for sale
    car_type = models.CharField(max_length=10, choices=[('sale', 'For Sale'), ('lease', 'For Lease')])
    seats = models.IntegerField()
    engine_type = models.CharField(max_length=50)
    fuel_type = models.CharField(max_length=50)
    size = models.CharField(max_length=50)  # e.g., compact, sedan
    image = models.ImageField(upload_to='cars/')
    approved = models.BooleanField(default=False)
    available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.model} - {self.plate}"

class ClientInquiry(models.Model):
    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name='inquiries')
    car = models.ForeignKey(Car, on_delete=models.CASCADE)
    inquiry_type = models.CharField(max_length=10, choices=[('buy', 'Buy'), ('hire', 'Hire')])
    client_name = models.CharField(max_length=100)
    client_phone = models.CharField(max_length=20)
    client_email = models.EmailField()
    client_id_number = models.CharField(max_length=10)
    message = models.TextField(blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)  # 24 hours from creation

    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(hours=24)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.client_name} - {self.car.model} ({self.inquiry_type})"

class Message(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='messages')
    content = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)

    def __str__(self):
        return f"Message to {self.user.username}: {self.content[:50]}"

class Booking(models.Model):
    inquiry = models.OneToOneField(ClientInquiry, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    total_days = models.IntegerField()
    base_price = models.DecimalField(max_digits=10, decimal_places=2)
    overtime_hours = models.IntegerField(default=0)
    overtime_charge = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Booking for {self.inquiry.car.model} by {self.inquiry.client_name}"

   