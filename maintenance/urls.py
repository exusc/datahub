
from django.urls import path
from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('dashboard', views.dashboard, name='dashboard'),
    path('dashboard/<str:owner_id>', views.dashboard, name='dashboard'),

    path('addscopes/<str:application_key>', views.AddScopesView.as_view(), name='addscopes'),
    
    path('setscope', views.setscope, name='setscope'),
    path('setscope/<str:scope_id>', views.setscope, name='setscope'),
    
    path('load', views.load, name='load'),

    path('check', views.check, name='check'),
    path('checkowner/<str:owner_id>', views.checkowner, name='checkowner'),
    path('checkarea/<str:area_id>', views.checkarea, name='checkarea'),

    path('switch_user/<int:user_id>', views.switch_user, name='switch_user'),
]
