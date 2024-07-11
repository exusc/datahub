from organization.models import Scope, Application
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
from datahub.settings import HUB_ALLOWED_OWNER_KEYS
from . forms import ScopeForm


def default_context(request):
    result = {}
    result['all_owners'] = Owner.objects.all().order_by('key')
    result['all_users'] = User.objects.all().order_by('first_name')
    result['all_scopes'] = request.user.scopes.all().order_by('key')
    result['all_containers'] = Container.objects.all().order_by(
        'containertype', 'key')
    return result


def dashboard(request, owner_id=None):
    context = default_context(request)
    if owner_id:
        owner = Owner.objects.get(id=owner_id)
    else:
        owner = request.user.owner
    context['owner'] = owner
    # context = default_context(request)
    context['number_areas'] = len(Area.objects.filter(owner=owner))
    context['number_scopes'] = len(Scope.objects.filter(owner=owner))
    return render(request, 'dashboard.html', context)


def setscope(request, scope_id=None):
    """ seleection and setting of the scope for the user """
    if scope_id:
        try:
            scope = Scope.objects.get(id=scope_id)
            request.user.use_scope = scope
            request.user.save()
        except:
            pass
    context = default_context(request)
    user_scopes = request.user.scopes.all().order_by('key')
    context['applications'] = {}
    for application in Application.objects.all().order_by('key'):
        app_scopes = user_scopes.filter(application=application).order_by('key')
        if len(app_scopes) > 0:
            context['applications'][application] = app_scopes
    return render(request, 'setscope.html', context)


def index(request):
    if not request.user.is_authenticated:
        user = User.objects.get(username='sys')
        login(request, user)
        return redirect(reverse("index"))
    context = default_context(request)
    context['LogEntrys'] = LogEntry.objects.all().filter(user=request.user)[
        0:5]
    return render(request, 'index.html', context)


"""
class UserView(View):
    def get(self, request, userid):
        context = {'user': User.objects.get(id=userid)}
        context['LogEntrys'] = LogEntry.objects.all().filter(user=userid)[0:5]
        return render(request, 'user.html', context)
"""


def switch_user(request, user_id):
    response = redirect(reverse("index"))

    # username = User.objects.get(id=userid).username
    # user = authenticate(request, username=username, password='???')
    user = User.objects.get(id=user_id)
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
        request.session[HUB_ALLOWED_OWNER_KEYS] = ownerlist

        # translation.activate(user.language)
        from django.conf import settings
        response.set_cookie(settings.LANGUAGE_COOKIE_NAME, user.language,)

    return response


# --------------------------------------------------------------------------------


class AddScopesView(View):

    def get(self, request, application_key):
        application = Application.objects.get(key=application_key)
        scope = Scope(application=application)
        form = ScopeForm(application=application, instance=scope)
        context = default_context(request)
        context['form'] = form
        context['application'] = application
        return render(request, 'form/form.html', context)

    def post(self, request, appkey):
        application = Application.objects.get(key=appkey)
        form = ScopeForm(application=application, data=request.POST, )
        if not form.is_valid():
            context = default_context(request)
            context['form'] = form
            context['application'] = application
            return render(request, 'form/form.html', context)
        form.save()
        return self.get(request, appkey)
