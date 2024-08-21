from django.contrib.auth.admin import UserAdmin, GroupAdmin
from django.contrib.admin.models import LogEntry
from django.contrib import admin
from django.utils import timezone
from .models import *
from django.utils.translation import gettext as _
from datahub.settings import HUB_ALLOWED_OWNER_KEYS


def allowed(request, set):
    """ Superusers are allowed to see every object.
        Normal users are restricted to their ALLOWED_OWNER
        TODO: Move to Model??
    """
    if request.user.is_superuser:
        return set
    if not '*' in request.session[HUB_ALLOWED_OWNER_KEYS]:
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
            "User": 21,
            "Scope": 22,
            "Group": 23,
            "Owner": 24,
            "Container": 31,
            "ContainerType": 32,
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
        list_display.remove("owner")
        return list_display

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "owner":
            kwargs["queryset"] = allowed(
                request, Owner.objects.all()).order_by('key')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class DataHubUserAdmin(UserAdmin):
    """ User must not give other users more rights then they have themselves """

    list_filter = ['groups', 'is_superuser', 'is_staff', 'is_active']
    list_display = ['username', 'first_name', 'last_name', 'language',
                    'is_staff', 'is_superuser', 'owner', 'is_active', ]
    # list_editable = ("is_active",)
    readonly_fields = ["last_login", 'use_scope']
    fieldsets = [
        (None, {'fields': [('username', 'owner'),
                           ('first_name', 'last_name'), 'email', ('language', 'use_scope')], }),
        ('Permissions', {'fields': [
         'is_active', 'is_staff', 'is_superuser', 'scopes', 'groups', ], }),
        ('Info', {'fields': ['last_login', ], }),
    ]
    filter_horizontal = ['scopes', 'groups']

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
        return allowed(request, super().get_queryset(request))

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """ Reduce list of selectable owner to owner of users scopes """
        if db_field.name == "owner":
            kwargs["queryset"] = allowed(request, Owner.objects.all().order_by('key'))
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        """ Reduce list of selectable scopes """
        if db_field.name == "scopes":
            kwargs["queryset"] = allowed(
                request, Scope.objects.all().order_by('key'))
        """ Reduce list of selectable groups """
        if db_field.name == "groups":
            if request.user.is_superuser or '*' in request.session[HUB_ALLOWED_OWNER_KEYS]:
                kwargs["queryset"] = Group.objects.all()
            else:
                kwargs["queryset"] = request.user.groups
        return super().formfield_for_manytomany(db_field, request, **kwargs)


class DataHubGroupAdmin(GroupAdmin):

    list_display = ['name', 'owner', ]
    fieldsets = [
        (None, {'fields': [('name', 'owner',), 'permissions', ], }),
        # ('History', {'fields': [('ctime', 'cuser'), ('utime', 'uuser')], },),
    ]

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
    list_display = ['key', 'desc', 'kanton', 'nr',
                    'ctime', 'cuser', 'owner', 'active', ]
    list_filter = ['cuser', 'kanton', 'active']
    fieldsets = [
        (None, {'fields': [('key', 'owner',),
         'active', 'desc', 'text', 'kanton', 'nr'], }),
        ('History', {'fields': [('ctime', 'cuser'), ('utime', 'uuser')], },),
    ]


class ApplicationAdmin(DatahubModelAdmin):
    search_fields = ['key', 'desc', ]
    list_display = ['key', 'desc',
                    'business_unit_1', 'business_unit_2', 'business_unit_3', 'owner', 'active']
    list_filter = ['active']
    fieldsets = [
        (None, {'fields': [('key', 'owner'), 'active', 'desc', 'text', ], }),
        ('Business Units', {'fields': [('business_unit_1', 'regex_1',),
                                       ('business_unit_2', 'regex_2',),
                                       ('business_unit_3', 'regex_3',),
                                       ('business_unit_4', 'regex_4',),
                                       ('business_unit_5', 'regex_5',),], }),
        ('History', {'fields': [('ctime', 'cuser'), ('utime', 'uuser')], },),
    ]


class ScopeAdmin(DatahubModelAdmin):

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """ Reduce list of owner dependent from superuser status """
        if db_field.name == "application":
            if request.user.is_superuser:
                kwargs["queryset"] = Application.objects.all()
            else:
                kwargs["queryset"] = Application.objects.filter(
                    owner=request.user.owner)
        """ Reduce list of selectable scopes to according type """
        if db_field.name == "org_scope":
            scopes = Scope.objects.filter(type='O')
            if not request.user.is_superuser:
                scopes = scopes.filter(application__owner=request.user.owner)
            kwargs["queryset"] = scopes
        if db_field.name == "app_scope":
            scopes = Scope.objects.filter(type='A')
            if not request.user.is_superuser:
                scopes = scopes.filter(application__owner=request.user.owner)
            kwargs["queryset"] = scopes
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    save_as = True
    search_fields = ['key', 'application__key', 'desc', 'hex', 'cuser']
    ordering = ['application__key', 'key',]
    list_filter = ['application', 'type', 'active']
    date_hierarchy = 'ctime'
    list_display = ['key', 'application',
                    'type', 'desc', 'org_scope', 'app_scope', 'hex', 'ctime', 'cuser', 'owner', 'active']
    fieldsets = [
        ('Combination', {'fields': [('application', 'type', 'hex', ),  'business_unit_1', 'business_unit_2',
         'business_unit_3', 'business_unit_4', 'business_unit_5', 'team', 'active'], }),
        ('Documentation', {'fields': ['desc'], }),
        ('Central Scopes', {'fields': ['org_scope', 'app_scope'], }),
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
                request, Container.objects.all()).filter(containertype__type=ContainerType.DATABASE)
        if db_field.name == "filestorage":
            kwargs["queryset"] = allowed(
                request, Container.objects.all()).filter(containertype__type=ContainerType.FILESTORAGE)
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
        ('Container', {'fields': [('database','schematables', 'schemaviews', ), 'filestorage'], }),
        ('History', {'fields': [('ctime', 'cuser'), ('utime', 'uuser')], },),
    ]


class ContainerAdmin(DatahubModelAdmin):
    search_fields = ['key', 'desc', ]
    ordering = ['key',]
    list_display = ['key', 'desc', 'containertype',
                    'connection', 'owner', 'active']
    list_filter = ['containertype']
    fieldsets = [
        (None, {'fields': [('key', 'owner',), 'active', 'desc',
         'containertype', 'connection', ], }),
        ('History', {'fields': [('ctime', 'cuser'), ('utime', 'uuser')], },),
    ]


class ContainerTypeAdmin(DatahubModelAdmin):
    ordering = ['key',]
    list_display = ['key', 'desc', 'type', 'owner', 'active']
    list_filter = ['type']
    fieldsets = [
        (None, {'fields': [('key', 'owner',),
         'active', 'desc', 'type', 'connection'], }),
        ('Scripts', {'fields': [('area_add', 'user_add', 'scope_add'), ], }),
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
    list_filter = ['user', 'content_type', 'action_flag']
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
datahub_admin_site.register(ContainerType, ContainerTypeAdmin)
datahub_admin_site.register(Scope, ScopeAdmin)
datahub_admin_site.register(LogEntry, LogEntryAdmin)
