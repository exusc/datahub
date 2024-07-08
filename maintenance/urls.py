
from django.urls import path
from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('dashboard', views.dashboard, name='dashboard'),
    path('dashboard/<str:ownerKey>', views.dashboard, name='dashboard'),
    path('addscopes/<str:appkey>', views.AddScopesView.as_view(), name='addscopes'),
    path('switch_user/<int:userid>', views.switch_user, name='switch_user'),
]
