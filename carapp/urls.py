from . import views
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.index, name='home'),
    path('about/', views.about, name='about'),
    path('contacts/', views.contact, name='contacts'),
    path('blog/sale/', views.blog_sale, name='blog_sale'),
    path('blog/hire/', views.blog_hire, name='blog_hire'),
    path('car/<int:car_id>/', views.car_detail, name='car_detail'),
    path('car/<int:car_id>/book/', views.inquire_car, {'inquiry_type': 'hire'}, name='book_car'),
    path('car/<int:car_id>/buy/', views.inquire_car, {'inquiry_type': 'buy'}, name='buy_car'),
    path('register/<str:role>/', views.register_profile, name='register_profile'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('client/dashboard/', views.client_dashboard, name='client_dashboard'),
    path('car/<int:car_id>/inquire/<str:inquiry_type>/', views.inquire_car, name='inquire_car'),
    path('inquiry/<int:inquiry_id>/payment/', views.make_payment, name='make_payment'),
    path('owner/dashboard/', views.owner_dashboard, name='owner_dashboard'),
    path('owner/register_car/', views.register_car, name='register_car'),
    path('owner/cancel_car/<int:car_id>/', views.cancel_car, name='cancel_car'),
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('approve_inquiry/<int:inquiry_id>/', views.approve_inquiry, name='approve_inquiry'),
    path('revoke_user/<int:user_id>/', views.revoke_user, name='revoke_user'),
    path('mpesa/callback/', views.mpesa_callback, name='mpesa_callback'),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)