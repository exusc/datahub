from django.shortcuts import render, redirect
from django.urls import reverse
from organization.models import Owner, User, Application, Area, Container
from django.contrib.auth import authenticate, login
from django.contrib.admin.models import LogEntry
from django.views import View
from datahub.settings import ALLOWED_OWNER


def default_context(request):
    result = {}
    result['all_owners'] = Owner.objects.all().order_by('key')
    result['all_users'] = User.objects.all().order_by('first_name')
    result['all_scopes'] = request.user.scopes.all().order_by('key')
    result['all_containers'] = Container.objects.all().order_by('containertype', 'key')
    return result

def index(request):
    if not request.user.is_authenticated:
        user = User.objects.get(username='sys')
        login(request, user)
        return redirect(reverse("index"))
    context = default_context(request)
    context['user'] = request.user
    context['LogEntrys'] = LogEntry.objects.all().filter(user=request.user)[
        0:5]
    return render(request, 'index.html', context)


def owner(request, key):
    owner = Owner.objects.get(key=key)
    context = default_context(request)
    context['owner'] = owner
    context['applications'] = Application.objects.filter(owner=owner)
    context['containers'] = Container.objects.filter(owner=owner)
    return render(request, 'owner.html', context)


def container(request, key):
    container = Container.objects.get(key=key)
    context = default_context(request)
    context['container'] = container
    areas = Area.objects.filter(database = container) | Area.objects.filter(filestorage = container)
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
