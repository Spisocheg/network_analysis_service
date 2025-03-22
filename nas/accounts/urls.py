from django.contrib.auth import views
from django.urls import path
from .views import LoginViewCustom


urlpatterns = [
    path('login/', LoginViewCustom.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout')
]
