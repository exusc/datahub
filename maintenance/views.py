from django.utils import timezone
from django import forms
from django.core.exceptions import ValidationError
from django.core import validators
from django.shortcuts import render, redirect
from django.urls import reverse
from organization.models import Owner, User, Application, Area, Container, Scope
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.admin.models import LogEntry
from django.contrib.messages import info, error
from django.views import View
from datahub.settings import HUB_ALLOWED_OWNER_KEYS
from django.db.utils import OperationalError
from organization.models import *
from . forms import ScopeForm
from . load import *
from . forms import SampleForm


@login_required(login_url="index")
def load(request):
    registered_classes = [Owner, ContainerType, Container,
                          Environment, Application, Area, Scope,  Group, User, ]

    if request.POST:
        for registered_class in registered_classes:
            name = registered_class._meta.verbose_name_plural
            action = request.POST.get(name)
            if action == 'Load':
                txt = f'{name} not loaded'
                if registered_class == Environment:
                    txt = EnvironmentLoader.load(request)
                if registered_class == Application:
                    txt = ApplicationLoader().load(request)
                if registered_class == Area:
                    txt = AreaLoader().load(request)
                if registered_class == Scope:
                    txt = ScopeLoader().load(request)
                if registered_class == Owner:
                    txt = OwnerLoader().load(request)
                if registered_class == Group:
                    txt = RoleLoader().load(request)
                if registered_class == User:
                    txt = UserLoader().load(request)
                if registered_class == ContainerType:
                    txt = ContainerTypeLoader().load(request)
                if registered_class == Container:
                    txt = ContainerLoader().load(request)
                info(request, txt)
            if action == 'Delete':
                txt = f'{name} not deleted'
                if registered_class == Owner:
                    txt = OwnerLoader().delete(request)
                if registered_class == Scope:
                    txt = ScopeLoader().delete(request)
                info(request, txt)

    context = default_context(request)
    classes = {}
    for registered_class in registered_classes:
        name = registered_class._meta.verbose_name_plural
        classes[name] = len(registered_class.objects.all())
    context['classes'] = classes
    return render(request, 'load.html', context)


@login_required(login_url="index")
def check(request):
    context = default_context(request)

    health_dbs = {}
    for database in Container.objects.filter(containertype__key__in=['SqlLite','PostGres']):
        try:
            schemas = database.schemas()
            health_dbs[database] = 'Access: ok, Schemas: ' + str(schemas)
        except OperationalError as err:
            health_dbs[database] = 'Access: ' + str(err)
    context['health_dbs'] = health_dbs

    health_areas = {}
    for area in Area.objects.all().order_by('application__key'):
        if (area.database.containertype.key in ['PostGres', 'SqlLite']):
            try:
                if area.schema() in area.database.schemas():
                    health_areas[area] = f'Schema "{area.schema()}" found'
                else:
                    health_areas[area] = f'Schema "{area.schema()}" not in Database "{area.database}"'
            except OperationalError as err:
                health_areas[area] = 'No access'
        else:
            health_areas[area] = 'Database type not suported'
    context['health_areas'] = health_areas

    return render(request, 'check.html', context)


def default_context(request):
    result = {}
    result['all_owners'] = Owner.objects.all().order_by('key')
    result['all_users'] = User.objects.all().order_by('first_name')
    result['all_scopes'] = request.user.get_scopes(separate_application=False)
    result['all_containers'] = Container.objects.all().order_by(
        'containertype', 'key')
    return result


@login_required(login_url="index")
@permission_required("organization.view_dashboard", login_url='index')
# @permission_required("organization.view_owner", login_url='index')
def dashboard(request, owner_id=None):
    context = default_context(request)
    if owner_id:
        owner = Owner.objects.get(id=owner_id)
        if request.user.is_superuser or '*' in request.session[HUB_ALLOWED_OWNER_KEYS] or owner.key in request.session[HUB_ALLOWED_OWNER_KEYS]:
            pass
        else:
            owner = request.user.owner
    else:
        owner = request.user.owner
    context['owner'] = owner
    # context = default_context(request)
    context['number_areas'] = len(Area.objects.filter(owner=owner))
    context['number_scopes'] = len(Scope.objects.filter(owner=owner))
    return render(request, 'dashboard.html', context)


@login_required(login_url="index")
def setscope(request, scope_id=None):
    """ selection and setting of the scope for the user """
    if scope_id:
        try:
            scope = Scope.objects.get(id=scope_id)
            request.user.use_scope = scope
            request.user.save()
            info(request, f'Scope is set to {scope} ({scope.desc})')
        except:
            pass
    context = default_context(request)
    context['applications'] = request.user.get_scopes()
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


@login_required(login_url="index")
def switch_user(request, user_id):
    response = redirect(reverse("index"))

    # username = User.objects.get(id=userid).username
    # user = authenticate(request, username=username, password='???')
    user = User.objects.get(id=user_id)
    if user:
        login(request, user)

        # list of allowed owner.keys for maintenence
        request.session[HUB_ALLOWED_OWNER_KEYS] = request.user.hub_owner()
        info(request, f'Switched to User: {user.first_name} {user.last_name}')

        # translation.activate(user.language)
        from django.conf import settings
        response.set_cookie(settings.LANGUAGE_COOKIE_NAME, user.language,)

        # if user-scope is inactive
        if user.use_scope and not user.use_scope.active:
            user.use_scope = None
            request.user.save()

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
