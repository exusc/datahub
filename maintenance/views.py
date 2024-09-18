from django.core.paginator import Paginator
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


M = 9
number_calls = 0


class Field():
    def __init__(self, value):
        self.value = value
        self.id = -1
        self.row = -1
        self.col = -1
        self.quad = -1
        self.opts = {}  # Möglichkeiten
        self.org = value != 0 # Original-Feld


class Sud():
    def __init__(self, values):
        # Aufbau Tabelle mit den Werten aus dem Grid
        self.grid = [[Field(col) for col in row] for row in values]
        # Grundeinstellung der Tabelle
        for row in range(9):
            for col in range(9):
                field = self.grid[row][col]
                field.id = row * 9 + col
                field.row = row
                field.col = col
                field.quad = 3 * (row // 3) + (col // 3)
                field.gray = field.quad % 2

    def field(self, id):
        if id < 0 or id > 80:
            return False
        return self.grid[id // 9][id % 9]


    def solve(self):
        values = [[col.value for col in row] for row in self.grid]
        if self._solve_part(values):
            return Sud(values)

    def _check_number(self, grid, row, col, num):
        """ Prüft, ob die Nummer an der Stelle erlaubt ist """
        # gibt es die Nummer schon in der row?
        for x in range(9):
            if grid[row][x] == num:
                return False
        # gibt es die Nummer schon in der col?
        for x in range(9):
            if grid[x][col] == num:
                return False
        # gibt es die Nummer schon in dem Quad?
        startRow = row - row % 3
        startCol = col - col % 3
        for i in range(3):
            for j in range(3):
                if grid[i + startRow][j + startCol] == num:
                    return False
        return True

    def _solve_part(self, grid, row=0, col=0) -> bool:
        """ Prüft, ob das Sudoku ab hier lösbar ist und setzt die Lösung im grid """
        global number_calls
        number_calls += 1
        # Wenn wir zu weit sind -> Ende
        if (row == M - 1 and col == M):
            return True
        # wenn col aus neuer Zeile ist, neue Zeile anfangen
        if col == M:
            row += 1
            col = 0
        # Wenn hier schon eine Zahl ist, löse das nächste Feld
        if grid[row][col] > 0:
            return self._solve_part(grid, row, col + 1)
        # Wenn das Feld unbekannt ist, probiere alle Zahlen aus
        for num in range(1, M + 1, 1):
            # Nimm nur Zahlen, die passen können
            if self._check_number(grid, row, col, num):
                grid[row][col] = num
                # Setz die Zahl rein
                # Wenn das Sudoku col1 dann lösbar ist -> ok
                if self._solve_part(grid, row, col + 1):
                    return True
            # sonst: Feld wieder zurücksetzen, nächste Zahl versuchen
            grid[row][col] = 0
        # Keine passende Zahl gefunden -> Sudoku ist nicht lösbar
        return False


def sud(request, field_id=-1):
    # field_id = Nummer des Feldes, das geklickt wurde
    # Soll allgemeiner die Knopf-Id werden
    context = default_context(request)
    values = [
        [0, 5, 6, 0, 4, 0, 0, 0, 0],
        [0, 0, 1, 5, 0, 0, 8, 0, 0],
        [8, 0, 0, 7, 3, 0, 0, 0, 0],
        [0, 8, 0, 0, 0, 0, 1, 9, 0],
        [0, 0, 3, 9, 0, 2, 7, 0, 0],
        [0, 1, 9, 0, 0, 0, 0, 6, 0],
        [0, 0, 0, 0, 9, 7, 0, 0, 1],
        [0, 0, 4, 0, 0, 5, 3, 0, 0],
        [0, 0, 0, 0, 2, 0, 6, 8, 0]
    ]
    sud = Sud(values)
    context['sud'] = sud
    if field_id > -1:
        context['mark_id'] = field_id
        mark_value = sud.field(field_id).value
        if mark_value > 0:
            context['mark_value'] = mark_value
    context['res'] = sud.solve()
    return render(request, 'sud.html', context)


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
def check(request, owner=None):
    context = default_context(request)
    context['owner'] = owner

    def result(health_dict, health_obj, level, msg, id='x'):
        """ Creates or updates the message object in health_dict
        """
        color = 'yellow'
        if level == 'O':
            color = 'green'
        if level == 'E':
            color = 'red'
        if not health_dict.get(health_obj):
            health_dict[health_obj] = {}
        obj = health_dict.get(health_obj)
        obj.update(
            {'badge_'+id: f'<span class="w3-badge w3-{color}">{level}</span>'})
        if level == 'O':
            obj.update({'ok': True})
        obj.update({'msg_'+id: msg})

    health_dbs = {}
    databases = Container.objects.filter(
        containertype__key__in=['SqlLite', 'PostGreSQL', ])
    if owner:
        owner_databases = []
        for area in Area.objects.all():
            if area.owner == owner and area.database in databases:
                owner_databases.append(area.database)
        databases = owner_databases

    for database in databases:
        try:
            database.schemas()  # Test Access to db
            result(health_dbs, database, 'O', 'Connection established')
        except OperationalError as error:
            result(health_dbs, database, 'E', str(error))
    context['health_dbs'] = health_dbs

    health_areas = {}
    areas = Area.objects.all().order_by('application__key')
    if owner:
        areas = areas.filter(owner=owner)
    for area in areas:
        if (area.database.containertype.key in ['PostGreSQL', ]):
            # schema_tables
            schema = 't'
            try:
                if area.schema_tables() in area.database.schemas():
                    result(health_areas, area, 'O',
                           f'Schema "{area.schema_tables()}" in database', schema)
                else:
                    result(health_areas, area, 'E',
                           f'Schema "{area.schema_tables()}" not in database', schema)
            except OperationalError as error:
                result(health_areas, area, 'I', 'No access', schema)
            # schema_views
            schema = 'v'
            try:
                if area.schema_views() in area.database.schemas():
                    result(health_areas, area, 'O',
                           f'Schema "{area.schema_views()}" in database', schema)
                else:
                    result(health_areas, area, 'E',
                           f'Schema "{area.schema_views()}" not in database', schema)
            except OperationalError as error:
                result(health_areas, area, 'I', 'No access', schema)
        else:
            result(health_areas, area, 'I',
                   f'Container type ({area.database.containertype.key}) not suported', 't')
            result(health_areas, area, 'I',
                   f'Container type ({area.database.containertype.key}) not suported', 'v')
    context['health_areas'] = health_areas

    return render(request, 'check.html', context)


@login_required(login_url="index")
def checkarea(request, area_id):
    area = Area.objects.get(id=area_id)
    context = default_context(request)
    context['area'] = area

    # Paginated list of tables
    tablenames = area.database.tablenames(area.schema_tables())
    paginator = Paginator(tablenames, 15)  # Show 15 tables per page.
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    context['page_obj'] = page_obj

    return render(request, 'checkarea.html', context)


@login_required(login_url="index")
def checkowner(request, owner_id):
    owner = Owner.objects.get(id=owner_id)
    return check(request, owner=owner)


def default_context(request):
    result = {}
    result['all_owners'] = Owner.objects.filter(active=True).order_by('key')
    result['all_users'] = User.objects.all().order_by(
        'first_name').filter(is_active=True)
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
    context['number_areas'] = len(
        Area.objects.filter(owner=owner).filter(active=True))
    context['number_scopes'] = len(
        Scope.objects.filter(owner=owner).filter(active=True))
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
