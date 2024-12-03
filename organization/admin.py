from django.contrib.auth.admin import UserAdmin, GroupAdmin
from django.contrib.admin.models import LogEntry
from django.contrib import admin
from django.utils import timezone
from .models import *
from django.contrib.auth.models import Group
from django.utils.translation import gettext as _
from django.utils.translation import ngettext
from datahub.settings import HUB_ALLOWED_OWNER_KEYS
from django.contrib import messages


def allowed(request, set):
    """ Superusers are allowed to see every object.
        Normal users are restricted to their ALLOWED_OWNER
        TODO: Move to Model??
    """
    if request.user.is_superuser or '*' in request.session[HUB_ALLOWED_OWNER_KEYS]:
        return set
    return set.filter(
        owner__key__in=request.session[HUB_ALLOWED_OWNER_KEYS])


class DatahubAdminSite(admin.AdminSite):

    site_header = _('DATA-Hub Maintenance')
    site_title = site_header

    def get_app_list(self, request, app_label=None):
        """ Sorts the list of Object within the admin menu        """
        ordering = {
            # "Report": 1,
            # "Order": 2,
            "Environment": 10,
            "Application": 11,
            "Area": 12,
            "Areascope": 13,
            "User": 21,
            "Group": 23,
            "Owner": 24,
            "Container": 31,
            "ContainerSystem": 32,
            "Scope": 40,
            "LogEntry": 0,
        }
        app_dict = self._build_app_dict(request, app_label)
        app_list = sorted(app_dict.values(), key=lambda x: x['name'].lower())

        # Sort the models alphabetically within each app.
        for app in app_list:
            app['models'].sort(key=lambda x: ordering[x['object_name']])

        return app_list


class DatahubModelAdmin(admin.ModelAdmin):
    """ Defaults for display """

    list_per_page = 15
    empty_value_display = '---'
    readonly_fields = ["ctime", "cuser", "utime", "uuser", ]

    def save_model(self, request, obj, form, change):
        if not change:
            obj.cuser = request.user.username
            obj.ctime = timezone.now()
        obj.uuser = request.user.username
        obj.utime = timezone.now()
        super().save_model(request, obj, form, change)

    def get_queryset(self, request):
        return allowed(request, super().get_queryset(request))

    def get_list_display(self, request):
        """ If user is just allowed to maintan one owner, he must not see the owners """
        list_display = list(self.list_display)
        if request.user.is_superuser or '*' in request.session[HUB_ALLOWED_OWNER_KEYS] or len(request.session[HUB_ALLOWED_OWNER_KEYS]) > 1:
            return list_display
        if "owner" in list_display:
            list_display.remove("owner")
        return list_display

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "owner":
            kwargs["queryset"] = allowed(
                request, Owner.objects.all()).order_by('key')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class DataHubUserAdmin(UserAdmin):
    """ User must not give other users more rights then they have themselves """

    def json_filename(self):
        """ Used to save and load Json data"""
        # return  f'../{self.__class__.__name__}-data.json'
        return f'../all-data.json'

    @admin.action(description=_("Unload all data as JSON"))
    def unload(self, request, queryset):
        def unld(file, data):
            file.write(AbstractDatahubModel.serialize(data))
            return len(data)
        count = 0
        with open(self.json_filename(), 'w') as file:
            count += unld(file, Owner.objects.all())
            count += unld(file, ContainerSystem.objects.all())
            count += unld(file, Container.objects.all())
            count += unld(file, Environment.objects.all())
            count += unld(file, Application.objects.all())
            count += unld(file, Area.objects.all())
            count += unld(file, Areascope.objects.all())
            count += unld(file, Group.objects.all())
            """ Don´t unload sys user """
            # from django.db.models import Q
            # count += unld(file, User.objects.filter(~Q(username='sys')))
            count += unld(file, User.objects.all())
        msg = ngettext(_(f"{count} object was successfully unloaded."),
                       _(f"{count} objects were successfully unloaded."),
                       count,)
        self.message_user(request, msg, messages.SUCCESS,)

    @admin.action(description=_("Load all data from JSON"))
    def load(self, request, queryset):
        with open(self.json_filename(), 'r') as file:
            data = file.read()
        count = AbstractDatahubModel.deserialize(data)
        msg = ngettext(_(f"{count} object was successfully loaded."),
                       _(f"{count} objects were successfully loaded."),
                       count,)
        self.message_user(request, msg, messages.SUCCESS,)
    
    actions = ['unload', 'load']

    list_filter = ['groups', 'is_superuser', 'is_staff', 'is_active']
    list_display = ['username', 'first_name', 'last_name', 'language',
                    'is_staff', 'is_superuser', 'owner', 'is_active', ]
    # list_editable = ("is_active",)
    readonly_fields = ["last_login", 'use_areascope']
    fieldsets = [
        (None, {'fields': [('username', 'owner'),
                           ('first_name', 'last_name'), 'email', ('language', 'use_areascope')], }),
        ('Permissions', {'fields': [
         'is_active', 'is_staff', 'is_superuser', 'areascopes', 'groups', ], }),
        ('Info', {'fields': ['last_login', ], }),
    ]
    filter_horizontal = ['areascopes', 'groups']

    def get_list_display(self, request):
        return DatahubModelAdmin.get_list_display(self, request)

    def save_model(self, request, obj, form, change):
        """ While saving, users owner will be the same as request.user.owner
            If user is not superuser, the new user also can't be a superuser
        """
        if not request.user.is_superuser:
            obj.owner = request.user.owner
            obj.is_superuser = False
        obj.save()

    def get_queryset(self, request):
        if request.user.is_superuser:
            self.actions = ['unload', 'load']
        else:
            self.actions = []
        return allowed(request, super().get_queryset(request))

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """ Reduce list of selectable owner to owner of users scopes """
        if db_field.name == "owner":
            kwargs["queryset"] = allowed(
                request, Owner.objects.all().order_by('key'))
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        """ Reduce list of selectable scopes """
        if db_field.name == "areascopes":
            # TODO: Auch Scopes anzeigen, die der User selbst hat
            kwargs["queryset"] = allowed(
                request, Areascope.objects.all().order_by('key'))
        """ Reduce list of selectable groups """
        if db_field.name == "groups":
            if request.user.is_superuser or '*' in request.session[HUB_ALLOWED_OWNER_KEYS]:
                kwargs["queryset"] = Group.objects.all()
            else:
                kwargs["queryset"] = request.user.groups
        return super().formfield_for_manytomany(db_field, request, **kwargs)


class DataHubGroupAdmin(GroupAdmin):

    list_display = ['name',]
    fieldsets = [
        (None, {'fields': [('name', ), 'permissions', ], }),
        # ('History', {'fields': [('ctime', 'cuser'), ('utime', 'uuser')], },),
    ]
    filter_horizontal = ['permissions']

    def get_list_display(self, request):
        return DatahubModelAdmin.get_list_display(self, request)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """ Reduce list of selectable owner to owner of users scopes """
        if db_field.name == "owner":
            kwargs["queryset"] = allowed(request, Owner.objects.all())
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class OwnerAdmin(DatahubModelAdmin):
    search_fields = ['key', 'desc', 'cuser']
    ordering = ['key',]
    date_hierarchy = 'ctime'
    list_display = ['key', 'desc', 'kanton', 'nr', 'owner', 'active', ]
    list_filter = ['cuser', 'kanton', 'active']
    fieldsets = [
        (None, {'fields': [('key', 'owner',),
         'active', 'desc', 'text', 'kanton', 'nr'], }),
        ('History', {'fields': [('ctime', 'cuser'), ('utime', 'uuser')], },),
    ]


class ApplicationAdmin(DatahubModelAdmin):
    search_fields = ['key', 'desc', ]
    list_display = ['key', 'desc',
                    'bu1_type', 'bu2_type', 'bu3_type', 'owner', 'active']
    list_filter = ['active']
    fieldsets = [
        (None, {'fields': [('key', 'owner'), 'active', 'desc', ], }),
        ('Business Unit Types', {'fields': [('bu1_type', 'bu1_field', 'regex_1',),
                                            ('bu2_type', 'bu2_field', 'regex_2',),
                                            ('bu3_type', 'bu3_field', 'regex_3',),
                                            ('bu4_type', 'bu4_field', 'regex_4',),
                                            ('bu5_type', 'bu5_field', 'regex_5',),
                                            ], }),
        ('History', {'fields': [('ctime', 'cuser'), ('utime', 'uuser')], },),
    ]


class AreascopeAdmin(DatahubModelAdmin):

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """ Reduce list of owner dependent from superuser status """
        if db_field.name == "area":
            if request.user.is_superuser:
                kwargs["queryset"] = Area.objects.all().order_by('key')
            else:
                kwargs["queryset"] = Area.objects.filter(
                    owner=request.user.owner)
        """ Reduce list of selectable scopes to according type """
        if db_field.name == "org_scope":
            scopes = Areascope.objects.filter(type='O')
            if not request.user.is_superuser:
                scopes = scopes.filter(area__owner=request.user.owner)
            kwargs["queryset"] = scopes
        if db_field.name == "app_scope":
            scopes = Areascope.objects.filter(type='A')
            if not request.user.is_superuser:
                scopes = scopes.filter(area__owner=request.user.owner)
            kwargs["queryset"] = scopes
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    # save_as = True
    search_fields = ['key', 'area__key', 'desc', 'hex', 'cuser']
    ordering = ['area__key', 'key',]
    list_filter = ['area', 'type', 'active']
    date_hierarchy = 'ctime'
    list_display = ['key', 'type', 'desc',
                    'org_scope', 'app_scope', 'owner', 'active']
    fieldsets = [
        ('Base Information', {'fields': [
         ('area', 'type', ), 'desc', 'active'], }),
        ('Business Units', {'fields': [('bu1_value', 'bu1_title'), ('bu2_value', 'bu2_title'), (
            'bu3_value', 'bu3_title'), ('bu4_value', 'bu4_title'), ('bu5_value', 'bu5_title'), ]}),
        ('Reporting Options', {'fields': [
         'team', 'org_scope', 'app_scope'], }),
        ('History', {'fields': [('ctime', 'cuser'), ('utime', 'uuser')], },),
    ]


class AreaAdmin(DatahubModelAdmin):

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "owner":
            kwargs["queryset"] = allowed(request, Owner.objects.all())
        if db_field.name == "application":
            kwargs["queryset"] = allowed(request, Application.objects.all())
        if db_field.name == "database":
            kwargs["queryset"] = allowed(
                request, Container.objects.all()).filter(containersystem__type=ContainerSystem.DATABASE)
        if db_field.name == "filestorage":
            kwargs["queryset"] = allowed(
                request, Container.objects.all()).filter(containersystem__type=ContainerSystem.FILESTORAGE)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    search_fields = ['key', 'application__key', 'desc']
    list_display = ['application', 'key', 'desc',
                    'database', 'schematables', 'schemaviews', 'filestorage', 'owner', 'active']
    list_display_links = ['key']
    ordering = ['application__key', 'key',]
    list_filter = ['application', 'active']
    fieldsets = [
        (None, {'fields': [('application', 'key', ),
         'active', 'desc', 'text', ], }),
        ('Container', {'fields': [
         ('database', 'schematables', 'schemaviews', ), 'filestorage'], }),
        ('History', {'fields': [('ctime', 'cuser'), ('utime', 'uuser')], },),
    ]


class ContainerAdmin(DatahubModelAdmin):
    search_fields = ['key', 'desc', ]
    ordering = ['key',]
    list_display = ['key', 'desc', 'containersystem',
                    'connection', 'owner', 'execute_scripts', 'active']
    list_filter = ['containersystem', 'active']
    fieldsets = [
        (None, {'fields': [('key', 'owner',), 'active', 'desc',
         'containersystem', 'connection', 'execute_scripts', ], }),
        ('History', {'fields': [('ctime', 'cuser'), ('utime', 'uuser')], },),
    ]


class ContainerSystemAdmin(DatahubModelAdmin):
    ordering = ['key',]
    list_display = ['key', 'desc', 'type', 'connection', 'owner', 'active']
    list_filter = ['type', 'active']
    fieldsets = [
        (None, {'fields': [('key', 'owner',),
         'active', 'desc', 'type', 'connection'], }),
        ('App Scripts', {'fields': [('area_add', ), ], }),
        ('Scope Scripts', {'fields': [('scope_add', 'scope_del'), ], }),
        ('User Scripts', {'fields': [('user_add', ), ], }),
        ('History', {'fields': [('ctime', 'cuser'), ('utime', 'uuser')], },),
    ]


class EnvironmentAdmin(DatahubModelAdmin):

    ordering = ['key',]
    search_fields = ['key', 'title', 'desc', 'natproc', ]
    list_display = ['key', 'title', 'desc', 'hostname',
                    'natproc', 'awlib', 'owner', 'active']
    list_filter = ['active']
    fieldsets = [
        (None, {'fields': [('key', 'owner',),
         'active', ('title', 'desc',), ], }),
        ('Host', {'fields': [('hostname', 'username', 'password'), ], }),
        ('AW', {'fields': ['ace_connect', ('natproc', 'awlib'), ], }),
        ('History', {'fields': [('ctime', 'cuser'), ('utime', 'uuser')], },),
    ]


class LogEntryAdmin(admin.ModelAdmin):
    # https://docs.djangoproject.com/en/5.0/ref/contrib/admin/#django.contrib.admin.models.LogEntry.action_flag
    list_per_page = 15
    list_filter = ['content_type', 'action_flag']
    search_fields = ['user__username', 'object_repr']
    list_display = ['action_time', 'user',
                    'content_type', 'object_repr', 'action_flag']


datahub_admin_site = DatahubAdminSite(name="datahub_admin")
datahub_admin_site.register(Environment, EnvironmentAdmin)
datahub_admin_site.register(User, DataHubUserAdmin)
datahub_admin_site.register(Group, DataHubGroupAdmin)
datahub_admin_site.register(Owner, OwnerAdmin)
datahub_admin_site.register(Application, ApplicationAdmin)
datahub_admin_site.register(Area, AreaAdmin)
datahub_admin_site.register(Container, ContainerAdmin)
datahub_admin_site.register(ContainerSystem, ContainerSystemAdmin)
datahub_admin_site.register(Areascope, AreascopeAdmin)
datahub_admin_site.register(LogEntry, LogEntryAdmin)
