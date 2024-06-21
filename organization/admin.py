from django.contrib.auth.admin import UserAdmin, GroupAdmin
from django.contrib import admin
from django.contrib.admin.models import LogEntry
from .models import *
from datetime import datetime


class DatahubAdminSite (admin.AdminSite):

    site_header = f'DATA-Hub'
    site_title = site_header

    def get_app_list(self, request):
        """ Sorts the list of Object within the admin menu        """
        ordering = {
            "Client": 1,
            "Group": 2,
            "User": 3,
            "Container": 4,
            "ContainerType": 5,
            "Application": 6,
            "Area": 7,
            "Scope": 8,
            "LogEntry": 9,
        }
        app_dict = self._build_app_dict(request)
        app_list = sorted(app_dict.values(), key=lambda x: x['name'].lower())

        # Sort the models alphabetically within each app.
        for app in app_list:
            app['models'].sort(key=lambda x: ordering[x['object_name']])

        return app_list


class DatahubModelAdmin (admin.ModelAdmin):
    """ Defaults für Model """

    list_per_page = 15
    empty_value_display = '---'
    readonly_fields = ["ctime", "cuser", "utime", "uuser", ]

    def save_model(self, request, obj, form, change):
        if not change:
            obj.cuser = request.user.username
            obj.ctime = datetime.now()
        obj.uuser = request.user.username
        obj.utime = datetime.now()
        super().save_model(request, obj, form, change)


class DataHubUserAdmin(UserAdmin):
    list_filter = ['client', 'groups']
    list_display = ['username', 'first_name', 'last_name',
                    'client', 'is_active', 'is_staff', 'is_superuser']
    readonly_fields = ["last_login",]
    fieldsets = [
        (None, {'fields': ['username',
         ('first_name', 'last_name'), 'email', 'client'], }),
        ('Permissions', {'fields': [
         'is_active', 'is_staff', 'is_superuser', 'scopes', 'groups'], }),
        ('Info', {'fields': ['last_login', ], }),
    ]
    filter_horizontal = ['scopes', 'groups']

    def get_queryset(self, request):
        """ 
        Superusers are allowed to see every object
        Normal users are restricted to their own client
        """
        queryset = super().get_queryset(request)
        if request.user.is_superuser:
            return queryset
        queryset = queryset.filter(client=request.user.client)
        return queryset


class ClientAdmin(DatahubModelAdmin):
    search_fields = ['key', 'desc']
    ordering = ['key',]
    list_display = ['key', 'desc', 'organization', ]
    list_filter = ['organization']
    fieldsets = [
        (None, {'fields': ['key', 'desc', 'text', ], }),
        ('Organization', {'fields': ['organization', ], }),
        ('History', {'fields': [('ctime', 'cuser'), ('utime', 'uuser')], },),
    ]

    def get_queryset(self, request):
        """ 
        Superusers are allowed to see every object
        Normal users are restricted to their own client
        """
        queryset = super().get_queryset(request)
        if request.user.is_superuser:
            return queryset
        queryset = queryset.filter(id=request.user.client.id)
        return queryset


class ApplicationAdmin(DatahubModelAdmin):
    search_fields = ['key', 'desc', ]
    list_display = ['key', 'desc', 'client',
                    'business_unit_1', 'business_unit_2']
    fieldsets = [
        (None, {'fields': ['key', 'desc', 'text', ], }),
        ('Ownership', {'fields': ['client', ], }),
        ('Business Units', {'fields': ['business_unit_1', 'business_unit_2',
         'business_unit_3', 'business_unit_4', 'business_unit_5',], }),
        ('History', {'fields': [('ctime', 'cuser'), ('utime', 'uuser')], },),
    ]

    def get_queryset(self, request):
        """ 
        Superusers are allowed to see every object
        Normal users are restricted to their own client
        """
        queryset = super().get_queryset(request)
        if request.user.is_superuser:
            return queryset
        queryset = queryset.filter(client=request.user.client)
        return queryset


class ScopeAdmin(DatahubModelAdmin):
    search_fields = ['key', 'application__key', 'desc']
    ordering = ['application__key', 'key',]
    list_display = ['key', 'application', 'desc', 'org_scope', 'app_scope']
    fieldsets = [
        ('Combination', {'fields': ['application', 'business_unit_1', 'business_unit_2',
         'business_unit_3', 'business_unit_4', 'business_unit_5', 'team'], }),
        ('Documentation', {'fields': ['desc'], }),
        ('Central Scopes', {'fields': ['org_scope', 'app_scope'], }),
        ('History', {'fields': [('ctime', 'cuser'), ('utime', 'uuser')], },),
    ]

    def save_model(self, request, obj, form, change):
        if not change:
            obj.cuser = request.user.username
            obj.ctime = datetime.now()
        obj.uuser = request.user.username
        obj.utime = datetime.now()
        obj.key = f'{obj.application.key.upper()}_{obj.business_unit_1.upper()}'
        if obj.business_unit_2:
            obj.key += f'_{obj.business_unit_2.upper()}'
        if obj.business_unit_3:
            obj.key += f'_{obj.business_unit_3.upper()}'
        if obj.business_unit_4:
            obj.key += f'_{obj.business_unit_4.upper()}'
        if obj.business_unit_5:
            obj.key += f'_{obj.business_unit_5.upper()}'
        if obj.team:
            obj.key += f'/{obj.team.upper()}'
        super().save_model(request, obj, form, change)

    def get_queryset(self, request):
        """ 
        Superusers are allowed to see every object
        Normal users are restricted to their own client
        """
        queryset = super().get_queryset(request)
        if request.user.is_superuser:
            return queryset
        queryset = queryset.filter(application__client=request.user.client)
        return queryset


class AreaAdmin(DatahubModelAdmin):
    list_display = ['application', 'key', 'desc', 'database', 'filestorage']
    ordering = ['application__key', 'key',]
    list_filter = ['application']
    fieldsets = [
        (None, {'fields': ['application', 'key', 'desc', 'text', ], }),
        ('Container', {'fields': ['database', 'filestorage'], }),
        ('History', {'fields': [('ctime', 'cuser'), ('utime', 'uuser')], },),
    ]

    def get_queryset(self, request):
        """ 
        Superusers are allowed to see every object
        Normal users are restricted to their own client
        """
        queryset = super().get_queryset(request)
        if request.user.is_superuser:
            return queryset
        queryset = queryset.filter(application__client=request.user.client)
        return queryset


class ContainerAdmin(DatahubModelAdmin):
    search_fields = ['key', 'desc', ]
    ordering = ['key',]
    list_display = ['key', 'desc', 'containertype', 'connection', 'client', ]
    list_filter = ['client', 'containertype']
    fieldsets = [
        (None, {'fields': [('key', 'desc'),
         'containertype', 'connection', ], }),
        ('Client', {'fields': ['client', ], }),
        ('History', {'fields': [('ctime', 'cuser'), ('utime', 'uuser')], },),
    ]


class ContainerTypeAdmin(DatahubModelAdmin):
    ordering = ['key',]
    list_display = ['key', 'desc', ]
    fieldsets = [
        (None, {'fields': [('key', 'desc'), 'type'], }),
        ('Scripts', {'fields': [('area_add', 'user_add'), ], }),
        ('History', {'fields': [('ctime', 'cuser'), ('utime', 'uuser')], },),
    ]


class LogEntryAdmin(admin.ModelAdmin):
    # https://docs.djangoproject.com/en/5.0/ref/contrib/admin/#django.contrib.admin.models.LogEntry.action_flag
    list_per_page = 15
    list_filter = ['user', 'content_type', 'action_flag']
    list_display = ['action_time', 'user',
                    'content_type', 'object_repr', 'action_flag']


datahub_admin_site = DatahubAdminSite(name="datahub_admin")
datahub_admin_site.register(User, DataHubUserAdmin)
datahub_admin_site.register(Group, GroupAdmin)
datahub_admin_site.register(Client, ClientAdmin)
datahub_admin_site.register(Application, ApplicationAdmin)
datahub_admin_site.register(Area, AreaAdmin)
datahub_admin_site.register(Container, ContainerAdmin)
datahub_admin_site.register(ContainerType, ContainerTypeAdmin)
datahub_admin_site.register(Scope, ScopeAdmin)
datahub_admin_site.register(LogEntry, LogEntryAdmin)
