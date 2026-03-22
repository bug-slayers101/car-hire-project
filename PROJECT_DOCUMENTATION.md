# Car Hire Project Documentation

## 1. Project Overview

This project is a Django-based car marketplace and booking system for three main user groups:

- Clients: browse cars, submit purchase or hire enquiries, receive approval, and make payments.
- Car owners: register cars, monitor approval state, and receive messages.
- Superusers: review and approve profiles, cars, and enquiries, and monitor bookings, M-Pesa transactions, and system messages.

The application supports:

- Car sale listings
- Car hire listings
- Owner registration and car submission
- Client registration and enquiries
- Booking overlap protection for hire requests
- M-Pesa payment initiation and callback handling
- Custom superuser dashboard


## 2. Technology Stack

- Backend: Django 4.2
- Language: Python
- Database: MySQL
- Media handling: Django `ImageField`
- Payment integration: Safaricom M-Pesa STK Push
- Frontend: Django templates, Bootstrap 4-style markup, custom CSS/JS assets


## 3. Project Structure

### Main folders

- `carhireproject/`: project-level Django configuration
- `carapp/`: core application containing models, views, forms, templates, admin, signals, and utilities
- `media/`: uploaded car images
- `myenv/`: local virtual environment

### Important files

- [manage.py](/abs/path/c:/Users/SIMON/Desktop/bugslayers/car-hire-project/manage.py): Django entry point
- [carhireproject/settings.py](/abs/path/c:/Users/SIMON/Desktop/bugslayers/car-hire-project/carhireproject/settings.py): settings, database config, static/media config, M-Pesa config
- [carhireproject/urls.py](/abs/path/c:/Users/SIMON/Desktop/bugslayers/car-hire-project/carhireproject/urls.py): root URL routing
- [carapp/models.py](/abs/path/c:/Users/SIMON/Desktop/bugslayers/car-hire-project/carapp/models.py): business data model
- [carapp/views.py](/abs/path/c:/Users/SIMON/Desktop/bugslayers/car-hire-project/carapp/views.py): application logic
- [carapp/forms.py](/abs/path/c:/Users/SIMON/Desktop/bugslayers/car-hire-project/carapp/forms.py): registration, login, inquiry, booking, and car forms
- [carapp/signals.py](/abs/path/c:/Users/SIMON/Desktop/bugslayers/car-hire-project/carapp/signals.py): automated approval/message side effects
- [carapp/mpesa_utils.py](/abs/path/c:/Users/SIMON/Desktop/bugslayers/car-hire-project/carapp/mpesa_utils.py): payment API helper
- [carapp/admin.py](/abs/path/c:/Users/SIMON/Desktop/bugslayers/car-hire-project/carapp/admin.py): Django admin registration


## 4. Core Data Model

### `Profile`

Extends Django `User` through a `OneToOneField`.

Key fields:

- `user`
- `role`: `owner` or `client`
- `phone_number`
- `id_number`
- `approved`
- `created_at`

Purpose:

- stores role-specific identity data
- controls approval before login access for normal users

### `Car`

Represents a vehicle listed by an owner.

Key fields:

- `owner`
- `model`
- `plate`
- `price`
- `car_type`: `sale` or `lease`
- `seats`
- `engine_type`
- `fuel_type`
- `size`
- `image`
- `approved`
- `available`

Purpose:

- powers the public listing pages
- supports either sale or hire use cases

### `ClientInquiry`

Represents a client request to buy or hire a car.

Key fields:

- `client`
- `car`
- `inquiry_type`: `buy` or `hire`
- client contact fields
- `message`
- `start_date`, `end_date`
- `total_price`
- `approved`
- `expires_at`

Behavior:

- automatically sets `expires_at` to 24 hours from creation if not provided
- now stores `total_price = car.price` for buy enquiries

### `Booking`

Created for approved hire workflows.

Key fields:

- `inquiry`
- `start_date`
- `end_date`
- `total_days`
- `base_price`
- `overtime_hours`
- `overtime_charge`
- `total_price`

Purpose:

- tracks the actual hire booking dates and price details

### `MpesaTransaction`

Represents an M-Pesa payment request and callback outcome.

Key fields:

- `inquiry`
- `merchant_request_id`
- `checkout_request_id`
- `result_code`
- `result_desc`
- `callback_metadata`
- `transaction_id`
- `amount`
- `phone_number`
- `status`
- timestamps

### `Message`

Internal notification model.

Key fields:

- `user`
- `content`
- `date`
- `read`

Purpose:

- approval notifications
- revocation notices
- payment result notices


## 5. User Roles and Main Flows

### 5.1 Public visitor flow

Visitors can:

- open the homepage
- browse sale cars via `/blog/sale/`
- browse hire cars via `/blog/hire/`
- open details for approved cars
- register as a client or owner
- log in

### 5.2 Client flow

Clients can:

- register using the client registration path
- wait for approval
- log in after activation
- open the client dashboard
- make hire enquiries
- make purchase enquiries
- receive messages
- make payment for approved enquiries

Client dashboard template:

- [carapp/templates/client_dashboard.html](/abs/path/c:/Users/SIMON/Desktop/bugslayers/car-hire-project/carapp/templates/client_dashboard.html)

### 5.3 Owner flow

Owners can:

- register using the owner registration path
- wait for approval
- log in after activation
- open the owner dashboard
- register a new car
- view the status of submitted cars
- remove a car when it has no active approved enquiries
- view messages

Owner dashboard template:

- [carapp/templates/owner_dashboard.html](/abs/path/c:/Users/SIMON/Desktop/bugslayers/car-hire-project/carapp/templates/owner_dashboard.html)

### 5.4 Superuser flow

Superusers can:

- log in from the normal login page
- access the custom admin dashboard
- approve client and owner profiles
- approve cars
- approve enquiries
- revoke users
- view bookings
- view M-Pesa transactions
- view messages

Custom admin dashboard template:

- [carapp/templates/admin_dashboard.html](/abs/path/c:/Users/SIMON/Desktop/bugslayers/car-hire-project/carapp/templates/admin_dashboard.html)


## 6. Application Pages and Routes

Defined mainly in [carapp/urls.py](/abs/path/c:/Users/SIMON/Desktop/bugslayers/car-hire-project/carapp/urls.py).

Important routes:

- `/`: homepage
- `/about/`
- `/contacts/`
- `/blog/sale/`
- `/blog/hire/`
- `/login/`
- `/logout/`
- `/register/<role>/`
- `/client/dashboard/`
- `/owner/dashboard/`
- `/owner/register_car/`
- `/dashboard/`: custom superuser dashboard
- `/inquiry/<id>/payment/`
- `/mpesa/callback/`


## 7. Homepage

The homepage has been customized into a full-width car showcase instead of the old split banner.

Current behavior:

- shows the company name prominently
- welcomes visitors
- uses a carousel of local car images
- includes descriptive slide text and action buttons

Template:

- [carapp/templates/index.html](/abs/path/c:/Users/SIMON/Desktop/bugslayers/car-hire-project/carapp/templates/index.html)


## 8. Authentication and Approval Logic

### Registration

Implemented in `register_profile()`.

Behavior:

- creates Django `User`
- marks the user inactive initially
- stores a `Profile`
- forces role from URL

### Login

Implemented in `login_view()`.

Behavior:

- superusers go to the custom admin dashboard
- owners go to owner dashboard
- clients go to client dashboard
- missing-profile users are blocked with an error

Important setting:

- `LOGIN_URL = '/login/'` in [carhireproject/settings.py](/abs/path/c:/Users/SIMON/Desktop/bugslayers/car-hire-project/carhireproject/settings.py)


## 9. Booking and Enquiry Logic

### Hire enquiry

When a client submits a hire enquiry:

- an inquiry is created
- a `BookingForm` is validated
- overlap is checked against approved bookings for the same car
- if dates clash, the user now stays on the form and sees an explicit booking conflict message
- if dates are valid, booking price fields are computed and stored

### Purchase enquiry

When a client submits a buy enquiry:

- `total_price` is set to the car’s sale price
- approval later marks the car unavailable


## 10. Payment Flow

Handled mainly in:

- `make_payment()` in [carapp/views.py](/abs/path/c:/Users/SIMON/Desktop/bugslayers/car-hire-project/carapp/views.py)
- [carapp/mpesa_utils.py](/abs/path/c:/Users/SIMON/Desktop/bugslayers/car-hire-project/carapp/mpesa_utils.py)

Current behavior:

- the user enters a phone number
- the system normalizes local formats like `07...` into `2547...`
- payable amount is derived from `inquiry.total_price`, with fallback to `car.price`
- an STK push is sent through M-Pesa
- a `MpesaTransaction` record is created with status `pending`
- callback updates transaction status later

### Callback processing

Handled by `mpesa_callback()`.

Behavior:

- parses Safaricom callback JSON
- locates the matching transaction
- updates result code, result description, metadata, transaction ID, and status
- creates client messages for success or failure


## 11. Signals and Automatic Side Effects

Defined in [carapp/signals.py](/abs/path/c:/Users/SIMON/Desktop/bugslayers/car-hire-project/carapp/signals.py).

### Profile approval signal

- activates the user account if profile is approved
- creates an approval message

### Car approval signal

- sends a message to the owner when a car is approved

### Inquiry approval signal

For buy enquiries:

- marks the car unavailable
- computes owner commission
- notifies client and owner

For hire enquiries:

- notifies client to proceed to payment


## 12. Admin and Dashboard Behavior

There are two admin layers:

### 12.1 Django admin

Defined in [carapp/admin.py](/abs/path/c:/Users/SIMON/Desktop/bugslayers/car-hire-project/carapp/admin.py).

It registers:

- `Profile`
- `Car`
- `ClientInquiry`
- `Message`
- `Booking`
- `MpesaTransaction`

### 12.2 Custom superuser dashboard

The custom dashboard is separate from Django admin and includes:

- client profiles
- owner profiles
- cars
- enquiries
- bookings
- M-Pesa transactions
- messages

Only superusers should access it.


## 13. Templates

Important templates include:

- [carapp/templates/base.html](/abs/path/c:/Users/SIMON/Desktop/bugslayers/car-hire-project/carapp/templates/base.html): shared layout and shared navbar
- [carapp/templates/index.html](/abs/path/c:/Users/SIMON/Desktop/bugslayers/car-hire-project/carapp/templates/index.html): homepage hero carousel
- [carapp/templates/login.html](/abs/path/c:/Users/SIMON/Desktop/bugslayers/car-hire-project/carapp/templates/login.html): standalone login page
- [carapp/templates/register.html](/abs/path/c:/Users/SIMON/Desktop/bugslayers/car-hire-project/carapp/templates/register.html)
- [carapp/templates/inquire.html](/abs/path/c:/Users/SIMON/Desktop/bugslayers/car-hire-project/carapp/templates/inquire.html)
- [carapp/templates/pay.html](/abs/path/c:/Users/SIMON/Desktop/bugslayers/car-hire-project/carapp/templates/pay.html)
- [carapp/templates/client_dashboard.html](/abs/path/c:/Users/SIMON/Desktop/bugslayers/car-hire-project/carapp/templates/client_dashboard.html)
- [carapp/templates/owner_dashboard.html](/abs/path/c:/Users/SIMON/Desktop/bugslayers/car-hire-project/carapp/templates/owner_dashboard.html)
- [carapp/templates/admin_dashboard.html](/abs/path/c:/Users/SIMON/Desktop/bugslayers/car-hire-project/carapp/templates/admin_dashboard.html)


## 14. Notable Fixes Already Applied

During maintenance, several issues were corrected:

- Django admin rendering compatibility patch for Python 3.14 in `carapp/apps.py`
- favicon path fixes
- custom superuser-only dashboard access
- owner/client/admin dashboard improvements
- booking conflict message on overlapping dates
- buy inquiry `total_price` fallback and persistence
- M-Pesa payment template fixes
- duplicate template block fixes in multiple templates
- navbar responsiveness improvements in shared layout
- homepage hero redesign
- signal bug fix for `Decimal * float`


## 15. Known Technical Risks and Caveats

### Django 4.2 + Python 3.14

The project currently runs Django 4.2 on Python 3.14, which is not a long-term ideal match. A compatibility patch was added, but upgrading Django to a version that officially supports Python 3.14 is recommended.

### Hard-coded secrets

M-Pesa credentials and Django `SECRET_KEY` are stored directly in settings. For production, these should move to environment variables.

### `DEBUG = True`

This is fine for development but unsafe for production.

### Open `ALLOWED_HOSTS`

`ALLOWED_HOSTS` is empty, which is fine for local development but not for deployment.

### Test setup issue

The test suite is currently blocked by a migration problem in [carapp/migrations/0002_drop_description.py](/abs/path/c:/Users/SIMON/Desktop/bugslayers/car-hire-project/carapp/migrations/0002_drop_description.py), which performs DDL in a way that breaks transactional test database setup on this backend.

### Contact form view

`contact()` currently has a placeholder POST handler and does not save or send submissions.


## 16. Environment and Configuration Notes

### Database

Configured for MySQL:

- database name: `car`
- host: `127.0.0.1`
- port: `3306`
- user: `root`

### Static and media

- `STATIC_URL = 'static/'`
- `MEDIA_URL = '/media/'`
- uploaded images are stored under `media/`


## 17. Suggested Next Improvements

- move secrets to environment variables
- upgrade Django to a Python-3.14-compatible release
- clean up and stabilize migrations
- add proper automated tests
- finish the contact form backend
- add payment reconciliation and retry tools
- improve owner/client message management
- add explicit payment status on enquiries


## 18. Quick Summary

This is a multi-role Django car marketplace and hire system with:

- approval-based onboarding
- owner car submission
- client buy and hire enquiries
- overlap-aware booking logic
- M-Pesa payment support
- notification messages
- a custom superuser operations dashboard

The project is functional and has been substantially stabilized, but it still has some infrastructure and maintainability work to do before it would be ready for production use.
