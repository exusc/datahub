from django.shortcuts import render, redirect
from django.urls import reverse
from organization.models import Owner, User, Application, Container
from django.contrib.auth import authenticate, login
from django.contrib.admin.models import LogEntry
from django.views.decorators.csrf import csrf_protect
from django.views import View


def index(request):
    context = {}
    context['owners'] = Owner.objects.all()
    context['users'] = User.objects.all()
    return render(request, 'index.html', context)


class UserView(View):
    def get(self, request, userid):
        context = {'user': User.objects.get(id=userid)}
        context['LogEntrys'] = LogEntry.objects.all().filter(user=userid)[0:5]
        return render(request, 'user.html', context)


def owner(request, key):
    owner = Owner.objects.get(key=key)
    context = {}
    context['owner'] = owner
    context['applications'] = Application.objects.filter(owner=owner)
    context['containers'] = Container.objects.filter(owner=owner)
    return render(request, 'owner.html', context)


def switch_user(request, userid):
    username = User.objects.get(id=userid).username
    user = authenticate(request, username=username, password='99999999')
    if user:
        login(request, user)
    return redirect(reverse("index"))
