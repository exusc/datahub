from django.utils import timezone
from .forms import SampleForm
from django.core.exceptions import ValidationError
from django.core import validators
from django import forms
from django.shortcuts import render, redirect
from django.urls import reverse
from organization.models import Owner, User, Application, Area, Container
from django.contrib.auth import authenticate, login
from django.contrib.admin.models import LogEntry
from django.views import View
from datahub.settings import ALLOWED_OWNER
from .forms import ScopeForm


def index(request):
    if not request.user.is_authenticated:
        user = User.objects.get(username='sys')
        login(request, user)
        return redirect(reverse("index"))
    context = {}
    context['owners'] = Owner.objects.all()
    context['users'] = User.objects.all()
    context['user'] = request.user
    context['LogEntrys'] = LogEntry.objects.all().filter(user=request.user)[
        0:5]
    return render(request, 'index.html', context)


def owner(request, key):
    owner = Owner.objects.get(key=key)
    context = {}
    context['owner'] = owner
    context['applications'] = Application.objects.filter(owner=owner)
    context['containers'] = Container.objects.filter(owner=owner)
    return render(request, 'owner.html', context)


def container(request, key):
    container = Container.objects.get(key=key)
    context = {}
    context['container'] = container
    # Area.objects.filter(filestorage = container)
    areas = Area.objects.filter(database=container)
    context['areas'] = areas
    return render(request, 'container.html', context)


class UserView(View):
    def get(self, request, userid):
        context = {'user': User.objects.get(id=userid)}
        context['LogEntrys'] = LogEntry.objects.all().filter(user=userid)[0:5]
        return render(request, 'user.html', context)


def switch_user(request, userid):
    response = redirect(reverse("index"))

    # username = User.objects.get(id=userid).username
    # user = authenticate(request, username=username, password='???')
    user = User.objects.get(id=userid)
    if user:
        login(request, user)
        # Creates the list of allowed owner.keys
        ownerlist = []
        for scope in request.user.scopes.filter(application__key='HUB'):
            if scope.business_unit_1 == '*':
                ownerlist = ['*']
                break
            try:
                owner = Owner.objects.get(key=scope.business_unit_1)
                ownerlist.append(owner.key)
            except:
                pass
        request.session[ALLOWED_OWNER] = ownerlist

        # translation.activate(user.language)
        from django.conf import settings
        response.set_cookie(settings.LANGUAGE_COOKIE_NAME, user.language,)

    return response


# --------------------------------------------------------------------------------
# Test Form


def sample_form(request):
    data = {}
    data['title'] = 'xx'
    data['zahl'] = '1111'
    data['datum'] = timezone.now()
    context = {'form': SampleForm(data)}
    return render(request, 'form/form.html', context)

from organization.models import Scope, Application

class AddScopeView(View):
    """ ToDo: sollte eine CreateView sein, die richtigen Validatoren verwenden und richtige T """
    application = Application.objects.get(key="HUB")

    def get(self, request):
        scope = Scope.objects.filter(application=AddScopeView.application)[0]
        form = ScopeForm(application=AddScopeView.application, instance=scope)
        context = {'form': form}
        return render(request, 'form/form.html', context)

    def post(self, request):
        form = ScopeForm(application=AddScopeView.application, data=request.POST, )
        if not form.is_valid():
            context = {'form': form}
            return render(request, 'form/form.html', context)
        return redirect(reverse("index"))
