from . import views
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    path('', views.index, name='home'),
    path('about/', views.about, name='about'),
    path('contacts/', views.contact, name='contacts'),
    path('blog/', views.blog, name='blog'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('carsdata/', views.carsdata, name='carsdata'),
    path('car/<int:id>/', views.car_detail, name='car_detail'),
    path('makepayment/<int:id>/', views.make_payment, name='makepayment'),
    path('clientdetail/', views.clientdetail, name='clientdetail'),
    path('clientdashboard/', views.client_dashboard, name='clientdashboard'),
    path('car/<int:id>/edit/', views.car_edit, name='car_edit'),
    path('car/<int:id>/delete/', views.car_delete, name='car_delete'),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)