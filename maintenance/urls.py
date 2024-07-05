
from django.urls import path
from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('dashboard', views.dashboard, name='dashboard'),
    path('overview', views.overview, name='overview'),
    path('owner/<str:key>', views.owner, name='owner'),
    path('addscopes/<str:appkey>', views.AddScopesView.as_view(), name='addscopes'),
    path('user/<int:userid>', views.UserView.as_view(), name='user'),
    path('container/<str:key>', views.container, name='container'),
    path('switch_user/<int:userid>', views.switch_user, name='switch_user'),
]
