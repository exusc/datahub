from django.shortcuts import render, redirect, reverse
from organization.models import Client, User
from django.contrib.auth import authenticate, login
from django.views.decorators.csrf import csrf_protect
from django.views import View


def index(request):
    context = {}
    context['clients']  = Client.objects.all()
    context['users'] = User.objects.all()
    return render(request, 'index.html', context)


class UserView(View):
    def get(self, request, userid):
        context = {'user' : User.objects.get(id=userid)}
        return render(request, 'user.html', context)


def client(request, key):
    context = {'client': Client.objects.get(key=key)}
    return render(request, 'client.html', context)


def switch_user(request, userid):
    username = User.objects.get(id=userid).username
    user = authenticate(request, username=username, password='99999999')
    if user:
        login(request, user)
    return redirect(reverse("index"))
