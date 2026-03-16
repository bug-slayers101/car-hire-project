from . import views
from django.urls import path
urlpatterns = [
    path('', views.index, name='home'),
    path('about/', views.about, name='about'),
    path('contacts/', views.contacts, name='contacts'),
    path('blog/', views.blog, name='blog'),
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('carsdata/', views.carsdata, name='carsdata'),
    path('makepayment/<int:id>/', views.make_payment, name='makepayment'),
    path('clientdetail/', views.clientdetail, name='clientdetail'),
    path('register', views.register, name='register'),
]