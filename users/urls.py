from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('signup/step1/', views.signup_step1, name='signup_step1'),
    path('signup/step2/', views.signup_step2, name='signup_step2'),
    path('signup/verify-otp/', views.verify_signup_otp, name='verify_signup_otp'),
    path('login/', views.login_view, name='login'),
    path('login/verify-otp/', views.verify_login_otp, name='verify_login_otp'),
    path('welcome/', views.welcome, name='welcome'),
    path('logout/', views.logout_view, name='logout'),
    path('demo/',views.demo, name='demo')
]
