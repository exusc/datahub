
from django.urls import path
from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('owner/<str:key>', views.owner, name='owner'),
    path('user/<int:userid>', views.UserView.as_view(), name='user'),
    path('switch_user/<int:userid>', views.switch_user, name='switch_user'),
]
