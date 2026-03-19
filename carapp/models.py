from django.db import models

# Create your models here.


class Contact(models.Model):
    name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20)
    email = models.EmailField()
    car_model = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    image = models.ImageField(upload_to='cars/')
    message = models.TextField(blank=True, null=True)

    approved = models.BooleanField(default=False)

    def __str__(self):
        return self.name


from django.contrib.auth.models import User


class ClientProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='client_profile')
    phone_number = models.CharField(max_length=20, blank=True)
    approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} ({'approved' if self.approved else 'pending'})"

   