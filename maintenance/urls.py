
from django.urls import path
from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('owner/<str:key>', views.owner, name='owner'),
    #path('add-scope', views.AddScopeView.as_view(), name='add_scope'),
    path('addscopes/<str:appkey>', views.AddScopesView.as_view(), name='addscopes'),
    path('form', views.sample_form, name='form'),
    path('user/<int:userid>', views.UserView.as_view(), name='user'),
    path('container/<str:key>', views.container, name='container'),
    path('switch_user/<int:userid>', views.switch_user, name='switch_user'),
]
