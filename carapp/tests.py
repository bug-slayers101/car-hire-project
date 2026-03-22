from datetime import date, timedelta
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Booking, Car, ClientInquiry, Profile


class BookingConflictTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(username='owner1', password='pass12345')
        self.client_user = User.objects.create_user(username='client1', password='pass12345')
        Profile.objects.create(user=self.owner, role='owner', phone_number='0700000001', id_number='1234567890', approved=True)
        Profile.objects.create(user=self.client_user, role='client', phone_number='0700000002', id_number='1234567891', approved=True)
        self.car = Car.objects.create(
            owner=self.owner,
            model='Test SUV',
            plate='KAA123A',
            price='5000.00',
            car_type='lease',
            seats=5,
            engine_type='2.0L',
            fuel_type='Petrol',
            size='SUV',
            image='cars/test.png',
            approved=True,
            available=True,
        )
        existing_inquiry = ClientInquiry.objects.create(
            client=self.client_user,
            car=self.car,
            inquiry_type='hire',
            client_name='Existing Booker',
            client_phone='0700000002',
            client_email='existing@example.com',
            client_id_number='1234567892',
            total_price='10000.00',
            approved=True,
            start_date=date.today() + timedelta(days=3),
            end_date=date.today() + timedelta(days=5),
        )
        Booking.objects.create(
            inquiry=existing_inquiry,
            start_date=date.today() + timedelta(days=3),
            end_date=date.today() + timedelta(days=5),
            total_days=2,
            base_price='10000.00',
            overtime_hours=0,
            overtime_charge='0.00',
            total_price='10000.00',
        )

    def test_overlapping_booking_shows_error_on_form(self):
        self.client.force_login(self.client_user)
        response = self.client.post(
            reverse('inquire_car', args=[self.car.id, 'hire']),
            {
                'client_name': 'New Client',
                'client_phone': '0700000003',
                'client_email': 'new@example.com',
                'client_id_number': '1234567893',
                'message': 'Need this car',
                'start_date': date.today() + timedelta(days=4),
                'end_date': date.today() + timedelta(days=6),
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'This car has already been booked for the selected dates.')
        self.assertEqual(ClientInquiry.objects.filter(client_name='New Client').count(), 0)
