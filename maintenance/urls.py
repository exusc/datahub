
from django.urls import path
from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('dashboard', views.dashboard, name='dashboard'),
    path('dashboard/<str:owner_id>', views.dashboard, name='dashboard'),

#    path('addscopes/<str:application_key>', views.AddScopesView.as_view(), name='addscopes'),
    
    path('setareascope', views.setareascope, name='setareascope'),
    path('setareascope/<str:areascope_id>', views.setareascope, name='setareascope'),
    
    path('load', views.load, name='load'),

    path('check', views.check, name='check'),
    path('checkowner/<str:owner_id>', views.checkowner, name='checkowner'),
    path('checkapplication/<str:application_id>', views.checkapplication, name='checkapplication'),

    path('area-rls/<str:area_id>', views.area_rls, name='area_rls'),

    path('switch_user/<int:user_id>', views.switch_user, name='switch_user'),
]
