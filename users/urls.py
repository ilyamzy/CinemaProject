from django.urls import path
from django.contrib.auth.views import LogoutView

from .views import LoginUser, RegisterUser, ProfileUser, AddManager


app_name = 'users'


urlpatterns = [
    path('login/', LoginUser.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='/'), name='logout'),
    path('register/', RegisterUser.as_view(), name='register'),
    path('manager/add/', AddManager.as_view(), name='add_manager'),
    path('profile/', ProfileUser.as_view(), name='profile'),
]
