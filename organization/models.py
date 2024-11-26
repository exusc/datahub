from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models, connections
from django.contrib.auth.models import AbstractUser, Group
from datahub.settings import LANGUAGES, HUB_OWNER_KEY, HUB_APPLICATION_KEY, DATABASES
from django.utils.translation import gettext as _
from django.db.models.signals import post_save, post_delete, m2m_changed
from django.dispatch import receiver
import uuid
import logging

db_logger = logging.getLogger('data')


PERMISSION_DIRECT_ACCESS = "db_read_access"
PERMISSION_UPLOAD_TEMPLATES = "upload_templates"
PERMISSION_DOWNLOAD_TEMPLATES = "download_templates"


class AbstractDatahubModel(models.Model):
    """ Default definition of all DATA-Hub objects
    """

    class Meta:
        abstract = True

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    active = models.BooleanField(_('active'), null=False, default=True,
                                 help_text=_("Inactive object is not available for end users"))

    desc = models.CharField(_('desc'), max_length=80, null=True, blank=True)
    text = models.TextField(_('text'), null=True, blank=True)

    ctime = models.DateTimeField(_('Create Time'), null=True, blank=True, )
    cuser = models.CharField(_('Create User'), max_length=8, null=True, blank=True,)
    utime = models.DateTimeField(_('Update Time'), null=True, blank=True, )
    uuser = models.CharField(_('Update User'), max_length=8, null=True, blank=True, )

    def __str__(self):
        """ Field 'Key' has to be defined in derived class
        """
        return f'{self.key}'


class Owner(AbstractDatahubModel):
    """ Used to assign ownership to applications and container.
        A owner might be owned by an other organization
    """
    class Meta:
        verbose_name = _("Owner")
        verbose_name_plural = _("Owners")
        ordering = ['key']
        permissions = [
            ("view_dashboard", "Can view Dashboard"),
        ]

    __hub = None

    owner = models.ForeignKey(
        'Owner', on_delete=models.PROTECT, null=True, blank=True, related_name='+',)
    key = models.CharField(_('key'), max_length=20, unique=True,)
    kanton = models.CharField(_('kanton'), max_length=2, null=True, blank=True)
    nr = models.IntegerField(_('kundennr'), null=True, blank=True)

    @classmethod
    def hub(cls):
        """ Returns the Owner Abraxas - must have the key "ABX"    """
        if not cls.__hub:
            try:
                cls.__hub = cls.objects.get(key=HUB_OWNER_KEY)
            except:
                cls.__hub = None
        return cls.__hub


class ContainerSystem(AbstractDatahubModel):
    """ ContainerSystem defines how the hub handels different activities like
        adding an area, adding an user, ...
    """
    class Meta:
        verbose_name = _("ContainerSystem")
        verbose_name_plural = _("ContainerSystems")

    DATABASE = 'DB'
    FILESTORAGE = 'FS'

    TYPE = {
        DATABASE: _("DataBase"),
        FILESTORAGE: _("FileStorage"),
    }

    owner = models.ForeignKey(
        to=Owner, on_delete=models.PROTECT, related_name='+',)
    key = models.CharField(_('key'), max_length=20, unique=True,)
    type = models.CharField(_('type'), max_length=2, choices=TYPE)
    connection = models.JSONField(_('Connection'), null=True,
                                  blank=True, help_text=_("Base information for connection like middleware"))
    area_add = models.TextField(_('area_add'), null=True,
                                blank=True, help_text=_("Script used to add an area to container"))
    user_add = models.TextField(_('user_add'), null=True,
                                blank=True, help_text=_("Script used to add a user to container"))
    user_del = models.TextField(_('user_del'), null=True,
                                blank=True, help_text=_("Script used to delete a user from container"))
    scope_add = models.TextField(_('scope_add'), null=True,
                                 blank=True, help_text=_("Script used to add a scope to container"))
    scope_del = models.TextField(_('scope_del'), null=True,
                                 blank=True, help_text=_("Script used to delete a scope from container"))
    user_to_scope = models.TextField(_('user_to_scope'), null=True,
                                     blank=True, help_text=_("Script used to link a user to a container"))
    user_from_scope = models.TextField(_('user_from_scope'), null=True,
                                       blank=True, help_text=_("Script used to unlink a user from a container"))


class Container(AbstractDatahubModel):
    """ Can contain data of multiple areas/application
        But we expect that every client wants to have his own containers

        TODO: implement methods add_scope, delete_scope using scripts from ContainerSystem
    """

    class Meta:
        verbose_name = _("Container")
        verbose_name_plural = _("Containers")
        ordering = ['key']
        permissions = [
            (PERMISSION_UPLOAD_TEMPLATES, "Is allowed to upload report templates"),
            (PERMISSION_DOWNLOAD_TEMPLATES,
             "Is allowed to download report templates"),
            (PERMISSION_DIRECT_ACCESS, "Is allowed connect to db and read data"),
        ]

    def __init__(self, *args, **kwargs):
        self.__schemas = None
        super().__init__(*args, **kwargs)

    owner = models.ForeignKey(
        to=Owner, on_delete=models.PROTECT, related_name='+',)
    key = models.CharField(_('key'), max_length=20, unique=True,)
    containersystem = models.ForeignKey(
        to=ContainerSystem, on_delete=models.PROTECT)
    connection = models.JSONField(_('Connection'), null=True,
                                  blank=True, help_text=_("To establish connection to container"))
    execute_scripts = models.BooleanField(_('execute_scripts'), null=False, default=False,
                                 help_text=_("Only if activated scripts will be executed"))


    def exec_filestorage(self, code, parms):
        """ Ausführen von Code im File Storage"""
        test = """
import os
# Create app path if not exists
app_path = os.path.join('{path}', '{app}')
if not os.path.exists(app_path):
    os.mkdir(app_path)
# Create area path if not exists
area_path = os.path.join(app_path, '{area}')
if not os.path.exists(area_path):
    os.mkdir(area_path)
# Create scope path if not exists
scope_path = os.path.join(area_path, '{scope}')
if not os.path.exists(scope_path):
    os.mkdir(scope_path)
"""     
        if code:
            formatted_code = code.format(**parms).strip()
            exec(formatted_code)

    def add_scope(self, area, scope_key):
        parms = {'app': area.application.key, 'area': area.key, 'scope': scope_key,}
        parms.update(self.connection)
        db_logger.info (
            f"{str(self):10} - Action:'{self.containersystem}.scope_add' - Parms: {parms}")
        if self.containersystem.type == ContainerSystem.FILESTORAGE:
            self.exec_filestorage(self.containersystem.scope_add, parms)

    def delete_scope(self, area, scope_key):
        parms = {'app': area.application.key,
                 'area': area.key, 'scope': scope_key}
        parms.update(self.connection)
        db_logger.info(
            f"{str(self):10} - Action:'{self.containersystem}.scope_delete' - Parms: {parms}")
        code = """
import os
# Create app path if not exists
app_path = os.path.join('{path}', '{app}')
area_path = os.path.join(app_path, '{area}')
scope_path = os.path.join(area_path, '{scope}')
if os.path.exists(scope_path):
    print('exists:', scope_path)
    if len(os.listdir(scope_path)) == 0:
        os.rmdir(scope_path)
"""

        if self.containersystem.type == ContainerSystem.FILESTORAGE:
            self.exec_filestorage(self.containersystem.scope_del, parms)

    def add_area(self, area, schemaname):
        parms = {'app': area.application.key,
                 'area': area.key, 'schema': schemaname}
        db_logger.info(
            f"{str(self):10} - Action:'{self.containersystem}.area_add' - Parms: {parms}")

    def add_user(self, user):
        parms = {'user': user.username}
        db_logger.info(
            f"{str(self):10} - Action:'{self.containersystem}.user_add' - Parms: {parms}")

    def delete_user(self, user):
        parms = {'user': user.username}
        db_logger.info(
            f"{str(self):10} - Action:'{self.containersystem}.user_delete' - Parms: {parms}")

    @property
    def __name(self):
        """ Returns a string used as identifier for connection """
        return str(self.id)

    def __connect(self):
        if not self.containersystem.type == 'DB':
            raise Exception(
                f'This container ({self.key}) is not type database')

        """ Adds the database to the settings.DATABASES, if it not exists
        """
        if not DATABASES.get(self.__name):
            # Create database dynamic based on 'data_template'
            db = DATABASES['data_template'].copy()
            # Set defaults dependent of containetype
            db.update(self.containersystem.connection)
            db.update(self.connection)
            # Hardcoded Defaults
            # db['USER'] = 'u...'
            # db['PASSWORD'] = 'p...'
            DATABASES[self.__name] = db

    def exec_sql(self, sql_string):

        # Raw Queries
        # https://docs.djangoproject.com/en/5.0/topics/db/sql/
        # direkt: https://docs.djangoproject.com/en/5.0/topics/db/sql/#executing-custom-sql-directly
        # https://docs.djangoproject.com/en/5.0/ref/models/querysets/

        if not self.containersystem.type == 'DB':
            raise Exception(
                f'This container ({self.key}) is not type database')

        # Connection aufbauen, falls sie noch nicht existiert
        self.__connect()

        with connections[self.__name].cursor() as cursor:
            cursor.execute(sql_string)
            rows = cursor.fetchall()
            return rows

            return [row[0] for row in rows]  # Return Col1
            return [col[0] for col in cursor.description]  # Return Header
            columns = [col[0] for col in cursor.description]
            # Return complete dict
            return [dict(zip(columns, row)) for row in rows]

    def schemas(self):
        if not self.__schemas:
            # PostGres:
            # rows = self.exec_sql("select nspname as schema from pg_catalog.pg_namespace where not nspowner = 10")
            # https://www.postgresql.org/docs/current/information-schema.html
            rows = self.exec_sql(
                "select schema_name from information_schema.schemata")
            self.__schemas = [row[0] for row in rows]
            # self.__schemas = self.exec_sql("select nspname as schema from pg_catalog.pg_namespace where not nspowner = 10")

            # SqlLite:
            # https://www2.sqlite.org/cvstrac/wiki?p=InformationSchema
            # Fields of sqlite_master: ['type', 'name', 'tbl_name', 'rootpage', 'sql']
            # self.__schemas = self.exec_sql("select tbl_name from sqlite_master where type = 'table'")

            # print(self.__schemas)

        return self.__schemas

    def tablenames(self, schema='dmo_rd_base'):
        # rows = self.exec_sql(f"select tablename from pg_catalog.pg_tables where schemaname = '{schema}' order by tablename")
        # https://www.postgresql.org/docs/current/information-schema.html
        rows = self.exec_sql(
            f"select table_name from information_schema.tables where table_schema = '{schema}' order by 1")
        tablenames = [row[0] for row in rows]
        return tablenames


class User(AbstractUser):
    """ If a user is assigned to an owner, that person is just allowed to work with owner related objects """
    class Meta:
        verbose_name = _("User")
        verbose_name_plural = _("Users")

    owner = models.ForeignKey(
        to=Owner, on_delete=models.PROTECT, null=True, blank=True,)
    scopes = models.ManyToManyField('Scope', blank=True)
    use_scope = models.ForeignKey(
        'Scope', on_delete=models.PROTECT, null=True, blank=True, related_name='+',)
    language = models.CharField(_('language'), max_length=5, choices=LANGUAGES, default='en',
                                help_text=_("Language used for DATA-Hub UI"))

#    def __init__(self, *args, **kwargs) -> None:
#        """ Used to cache permissions to detect changes of permissions """
#        super().__init__(*args, **kwargs)
#        self.cached_permission_direct_access = self.has_permission(PERMISSION_DIRECT_ACCESS) if len(args) > 0 else False

    def get_scopes(self, detailed=False, separate_application=True):
        """ Returns a dict of all active Scopes the user can choose
            * scope is replaced by all possible Scopes
            separate_application -> separate dict per application; else one dict for all scopes
        TODO: Test cases needed
        """
        result = {}
        all_scopes = self.scopes.all().filter(active=True).order_by(
            'key').filter(application__active=True)
        if not separate_application:
            return all_scopes
        for scope in all_scopes:
            application = result.get(scope.application)
            if application == None:
                result[scope.application] = all_scopes.filter(
                    application=scope.application)
        return result

    def hub_owner(self):
        """ Return the list of owner the user is allowed to maintain in the Hub """
        ownerlist = []
        for scope in self.scopes.filter(application=Application.hub()).filter(active=True):
            if scope.business_unit_1 == '*':
                ownerlist = ['*']
                break
            try:
                owner = Owner.objects.get(key=scope.business_unit_1)
                ownerlist.append(owner.key)
            except:
                pass
        return ownerlist

    def has_permission(self, permission: str):
        """ Checks permissions of user linked by groups, not directly to user """
        for group in self.groups.all():
            if len(group.permissions.filter(codename=permission)) > 0:
                return True
        return False


class Group(Group):
    class Meta:
        verbose_name = _("Role")
        verbose_name_plural = _("Roles")

    owner = models.ForeignKey(
        to=Owner, on_delete=models.PROTECT, null=True, blank=True,)


class Application(AbstractDatahubModel):
    """ Business units are defined on application level - in this prototype its just a simple definition
        For real implementation this mut be a separate object with information about allowed values ...
    """
    class Meta:
        verbose_name = _("Application")
        verbose_name_plural = _("Applications")
        ordering = ['key']

    __hub = None

    owner = models.ForeignKey(to=Owner, on_delete=models.PROTECT)
    key = models.CharField(_('key'), max_length=20, unique=True,)
    business_unit_1 = models.CharField(
        _('business_unit_1'), max_length=80, null=True, blank=True)
    business_unit_2 = models.CharField(
        _('business_unit_2'), max_length=80, null=True, blank=True)
    business_unit_3 = models.CharField(
        _('business_unit_3'), max_length=80, null=True, blank=True)
    business_unit_4 = models.CharField(
        _('business_unit_4'), max_length=80, null=True, blank=True)
    business_unit_5 = models.CharField(
        _('business_unit_5'), max_length=80, null=True, blank=True)

    regex_1 = models.CharField(
        _('regex_1'), max_length=80, null=True, blank=True)
    regex_2 = models.CharField(
        _('regex_2'), max_length=80, null=True, blank=True)
    regex_3 = models.CharField(
        _('regex_3'), max_length=80, null=True, blank=True)
    regex_4 = models.CharField(
        _('regex_4'), max_length=80, null=True, blank=True)
    regex_5 = models.CharField(
        _('regex_5'), max_length=80, null=True, blank=True)

    @classmethod
    def hub(cls):
        """ Returns the Application of the Data_Hub - must have the Key "HUB"    """
        if not cls.__hub:
            try:
                cls.__hub = cls.objects.get(key=HUB_APPLICATION_KEY)
            except:
                cls.__hub = None
        return cls.__hub


class Area(AbstractDatahubModel):
    """ Each area belongs to an application and can have its own database and file storage"""
    class Meta:
        verbose_name = _("Area")
        verbose_name_plural = _("Areas")
        unique_together = ['application', 'key']

    owner = models.ForeignKey(
        to=Owner, on_delete=models.PROTECT, related_name='+',)
    key = models.CharField(_('key'), max_length=20)
    application = models.ForeignKey(to=Application, on_delete=models.PROTECT)
    database = models.ForeignKey(to=Container, on_delete=models.PROTECT,
                                 related_name='+', help_text=_("To store structured data"))
    filestorage = models.ForeignKey(
        to=Container, on_delete=models.PROTECT, related_name='+', help_text=_("To store files"))
    schematables = models.CharField(_('schematables'), max_length=40, null=True,
                                    blank=True, help_text='Overwrite default (app.key_area.key_base)')
    schemaviews = models.CharField(_('schemaviews'), max_length=40, null=True,
                                   blank=True, help_text='Overwrite default (app.key_area.key)')

    def __init__(self, *args, **kwargs) -> None:
        """ Used to cache original schema values to detect changes within signal method. Set to blank if object is new """
        super().__init__(*args, **kwargs)
        self.cached_schema_tables = self.schema_tables() if len(args) > 0 else ''
        self.cached_schema_views = self.schema_views() if len(args) > 0 else ''

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        self.owner = self.application.owner
        super().save(force_insert, force_update, using, update_fields)

    def schema_tables(self):
        return self.schematables if self.schematables else f'{self.application.key}_{self.key}_base'.lower()

    def schema_views(self):
        return self.schemaviews if self.schemaviews else f'{self.application.key}_{self.key}'.lower()

    def __str__(self):
        return f'{self.application}_{self.key}'


class Areascope(AbstractDatahubModel):
    """ Areascopes are linked to areas and use the BU-definition of the application
        BUs will be checked by validator
        https://docs.djangoproject.com/en/5.0/ref/validators/
    """
    class Meta:
        verbose_name = _("Areascope")
        verbose_name_plural = _("Areascopes")

    TYPE = {
        "S": _("Standard"),
        "O": _("Org scope"),
        "A": _("App scope"),
        "T": _("Test scope"),
    }

    owner = models.ForeignKey(
        to=Owner, on_delete=models.PROTECT, related_name='+',)
    key = models.CharField(_('key'), max_length=80, unique=True, default="tbd")
    hex = models.CharField(_('hex'), max_length=8, null=True,
                           blank=True, help_text=_("Hex value for AW data"))
    type = models.CharField(_('type'), max_length=1, choices=TYPE, default='S',
                            help_text=_("Defines how scope can be used"))
    area = models.ForeignKey(to=Area, on_delete=models.PROTECT)
    bu1_value = models.CharField(_('bu1_value'), max_length=80, null=True, blank=True,)
    bu2_value = models.CharField(_('bu2_value'), max_length=80, null=True, blank=True,)
    bu3_value = models.CharField(_('bu3_value'), max_length=80, null=True, blank=True,)
    bu4_value = models.CharField(_('bu4_value'), max_length=80, null=True, blank=True,)
    bu5_value = models.CharField(_('bu5_value'), max_length=80, null=True, blank=True,)
    bu1_title = models.CharField(_('bu1_title'), max_length=80, null=True, blank=True,)
    bu2_title = models.CharField(_('bu2_title'), max_length=80, null=True, blank=True,)
    bu3_title = models.CharField(_('bu3_title'), max_length=80, null=True, blank=True,)
    bu4_title = models.CharField(_('bu4_title'), max_length=80, null=True, blank=True,)
    bu5_title = models.CharField(_('bu5_title'), max_length=80, null=True, blank=True,)
    team = models.CharField(_('team'), max_length=80, null=True, blank=True)
    org_scope = models.ForeignKey('Areascope', on_delete=models.PROTECT, null=True, blank=True, related_name='+',
                                  help_text=_("Here are the standard templates created by the client"))
    app_scope = models.ForeignKey('Areascope', on_delete=models.PROTECT, null=True, blank=True, related_name='+',
                                  help_text=_("Here are the standard templates created by Abraxas or other provider"))

    def __init__(self, *args, **kwargs) -> None:
        """ Used to cache original key to detect changes within signal method. Set to blank if object is new """
        super().__init__(*args, **kwargs)
        self.cached_key = self.key if len(args) > 0 else ''

    def full_clean(self, exclude=None, validate_unique=True, validate_constraints=True):
        """ Before the data is cleaned a validator for Business-Units will be added / replaced
            https://docs.djangoproject.com/en/5.0/ref/forms/validation/
        """
        for f in self._meta.fields:
            if f.name == 'bu1_value' and self.area.application.regex_1:
                for vali in f.validators:
                    if type(vali) == RegexValidator:
                        f.validators.remove(vali)
                f.validators.append(RegexValidator(
                    regex=self.area.application.regex_1))
            if f.name == 'bu2_value' and self.area.application.regex_2:
                for vali in f.validators:
                    if type(vali) == RegexValidator:
                        f.validators.remove(vali)
                f.validators.append(RegexValidator(
                    regex=self.area.application.regex_2))
            if f.name == 'bu3_value' and self.area.application.regex_3:
                for vali in f.validators:
                    if type(vali) == RegexValidator:
                        f.validators.remove(vali)
                f.validators.append(RegexValidator(
                    regex=self.area.application.regex_3))
            if f.name == 'bu4_value' and self.area.application.regex_4:
                for vali in f.validators:
                    if type(vali) == RegexValidator:
                        f.validators.remove(vali)
                f.validators.append(RegexValidator(
                    regex=self.area.application.regex_4))
            if f.name == 'bu5_value' and self.area.application.regex_5:
                for vali in f.validators:
                    if type(vali) == RegexValidator:
                        f.validators.remove(vali)
                f.validators.append(RegexValidator(
                    regex=self.area.application.regex_5))

        super().full_clean(exclude=exclude, validate_unique=validate_unique,
                           validate_constraints=validate_constraints)

    def clean(self):

        def append(delimiter,value, title):
            if title:
                self.key += f'{delimiter}{title.lower()}'
            elif value:
                self.key += f'{delimiter}{value.lower()}'

        self.owner = self.area.owner
        """ Creates the key based on the BUs
        """

        self.key = f'{self.area}'
        append('/',self.bu1_value, self.bu1_title)
        append('_',self.bu2_value, self.bu2_title)
        append('_',self.bu3_value, self.bu3_title)
        append('_',self.bu4_value, self.bu4_title)
        append('_',self.bu5_value, self.bu5_title)
        if self.team:
            self.key += f'/{self.team.lower()}'

        """ Check if scope already exists """
        if self._state.adding and Scope.objects.filter(key=self.key):
            raise ValidationError(
                _("Scope: %(value)s already exists."),
                code="invalid",
                params={"value": self.key},
            )


class Scope(AbstractDatahubModel):
    """ Scopes are linked to application and used from all areas within these application
        BUs will be checked by validator
        https://docs.djangoproject.com/en/5.0/ref/validators/
    """
    class Meta:
        verbose_name = _("Scope")
        verbose_name_plural = _("Scopes")

    TYPE = {
        "S": _("Standard"),
        "O": _("Org scope"),
        "A": _("App scope"),
        "T": _("Test scope"),
    }

    owner = models.ForeignKey(
        to=Owner, on_delete=models.PROTECT, related_name='+',)
    key = models.CharField(_('key'), max_length=80, unique=True, default="tbd")
    hex = models.CharField(_('hex'), max_length=8, null=True,
                           blank=True, help_text=_("Hex value for AW data"))
    type = models.CharField(_('type'), max_length=1, choices=TYPE, default='S',
                            help_text=_("Defines how scope can be used"))
    application = models.ForeignKey(to=Application, on_delete=models.PROTECT)
    business_unit_1 = models.CharField(
        _('business_unit_1'), max_length=80, null=True, blank=True,)
    business_unit_2 = models.CharField(
        _('business_unit_2'), max_length=80, null=True, blank=True)
    business_unit_3 = models.CharField(
        _('business_unit_3'), max_length=80, null=True, blank=True)
    business_unit_4 = models.CharField(
        _('business_unit_4'), max_length=80, null=True, blank=True)
    business_unit_5 = models.CharField(
        _('business_unit_5'), max_length=80, null=True, blank=True)
    team = models.CharField(_('team'), max_length=80, null=True, blank=True)
    org_scope = models.ForeignKey('Scope', on_delete=models.PROTECT, null=True, blank=True, related_name='+',
                                  help_text=_("Here are the standard templates created by the client"))
    app_scope = models.ForeignKey('Scope', on_delete=models.PROTECT, null=True, blank=True, related_name='+',
                                  help_text=_("Here are the standard templates created by Abraxas or other provider"))

    def __init__(self, *args, **kwargs) -> None:
        """ Used to cache original key to detect changes within signal method. Set to blank if object is new """
        super().__init__(*args, **kwargs)
        self.cached_key = self.key if len(args) > 0 else ''

    def full_clean(self, exclude=None, validate_unique=True, validate_constraints=True):
        """ Before the data is cleaned a validator for Business-Units will be added / replaced
            https://docs.djangoproject.com/en/5.0/ref/forms/validation/
        """
        for f in self._meta.fields:
            if f.name == 'business_unit_1' and self.application.regex_1:
                for vali in f.validators:
                    if type(vali) == RegexValidator:
                        f.validators.remove(vali)
                f.validators.append(RegexValidator(
                    regex=self.application.regex_1))
            if f.name == 'business_unit_2' and self.application.regex_2:
                for vali in f.validators:
                    if type(vali) == RegexValidator:
                        f.validators.remove(vali)
                f.validators.append(RegexValidator(
                    regex=self.application.regex_2))
            if f.name == 'business_unit_3' and self.application.regex_3:
                for vali in f.validators:
                    if type(vali) == RegexValidator:
                        f.validators.remove(vali)
                f.validators.append(RegexValidator(
                    regex=self.application.regex_3))
            if f.name == 'business_unit_4' and self.application.regex_4:
                for vali in f.validators:
                    if type(vali) == RegexValidator:
                        f.validators.remove(vali)
                f.validators.append(RegexValidator(
                    regex=self.application.regex_4))
            if f.name == 'business_unit_5' and self.application.regex_5:
                for vali in f.validators:
                    if type(vali) == RegexValidator:
                        f.validators.remove(vali)
                f.validators.append(RegexValidator(
                    regex=self.application.regex_5))
        super().full_clean(exclude=exclude, validate_unique=validate_unique,
                           validate_constraints=validate_constraints)

    def clean(self):

        self.owner = self.application.owner
        """ Creates the key based on the BUs
        """

        self.key = f'{self.application.key.upper()}'
        if self.business_unit_1:
            self.key += f'_{self.business_unit_1.upper()}'
        if self.business_unit_2:
            self.key += f'_{self.business_unit_2.upper()}'
        if self.business_unit_3:
            self.key += f'_{self.business_unit_3.upper()}'
        if self.business_unit_4:
            self.key += f'_{self.business_unit_4.upper()}'
        if self.business_unit_5:
            self.key += f'_{self.business_unit_5.upper()}'
        if self.team:
            self.key += f'/{self.team.upper()}'

        """ Check if scope already exists """
        if self._state.adding and Scope.objects.filter(key=self.key):
            raise ValidationError(
                _("Scope: %(value)s already exists."),
                code="invalid",
                params={"value": self.key},
            )


class Environment(AbstractDatahubModel):
    class Meta:
        verbose_name = _("Environment")
        verbose_name_plural = _("Environments")

    owner = models.ForeignKey(
        to=Owner, on_delete=models.PROTECT, related_name='+',)
    key = models.CharField(_('key'), max_length=2,
                           null=True, blank=True, unique=True,)
    title = models.CharField(_('title'), max_length=10)
    hostname = models.CharField(
        _('hostname'), max_length=64, null=True, blank=True)
    username = models.CharField(
        _('username'), max_length=8, null=True, blank=True)
    password = models.CharField(
        _('password'), max_length=8, null=True, blank=True)
    ace_connect = models.CharField(
        _('ace_connect'), max_length=256, null=True, blank=True, )

    natproc = models.CharField(
        _('natproc'), max_length=8, null=True, blank=True, help_text=_(
            'Used in batch job.'))

    awlib = models.CharField(
        _('awlib'), max_length=8, null=True, blank=True, help_text=_(
            'Used in batch job.'))


"""
   Methods save_* are triggered by changes of DATA-Hub objects and will implement actions on db
"""


@receiver(post_save, sender=Area)
def receive_save_area(sender, instance: Area, created, **kwargs):
    """ Only changes of schema names are relevant 
        Trigger actions: add new schema to database, no actions in filestorage
    """

    if instance.schema_tables() != instance.cached_schema_tables:
        instance.database.add_area(instance, instance.schema_tables())
    if instance.schema_views() != instance.cached_schema_views:
        instance.database.add_area(instance, instance.schema_views())

    if created:
        for scope in instance.application.scope_set.all():
            instance.database.add_scope(instance, scope.key)
            instance.filestorage.add_scope(instance, scope.key)


@receiver(post_save, sender=Scope)
def receive_save_scope(sender, instance: Scope, created, **kwargs):
    """ Changes of business units are relevant 
        Triggers actions: deletion of old scope and adding new scope
    """

    def info_all_areas(scope: Scope, scope_key, delete=False):
        for area in scope.application.area_set.all():
            if delete:
                area.database.delete_scope(area, scope_key)
                area.filestorage.delete_scope(area, scope_key)
            else:
                area.database.add_scope(area, scope_key)
                area.filestorage.add_scope(area, scope_key)

    # Only changes of key are relevant
    if (instance.key != instance.cached_key):
        if instance.cached_key:
            info_all_areas(instance, instance.cached_key, delete=True)
        info_all_areas(instance, instance.key)


@receiver(post_delete, sender=Scope)
def receive_delete_scope(sender, instance: Scope, **kwargs):
    """ Deletion of scopes will be executed in containers """
    for area in instance.application.area_set.all():
        area.database.delete_scope(area, instance.key)
        area.filestorage.delete_scope(area, instance.key)


@receiver(signal=m2m_changed, sender=User.groups.through)
def receive_group_assignments(instance: User, action, reverse, model, pk_set, using, *args, **kwargs):
    """ Falls beim User Gruppen hinzugefügt oder geändert wurden, ist zu prüfen:
        Remove von Gruppen:
        1. hat eine der Gruppen direct access?
        2. hat der User jetzt kein direkt access mehr -> direct access entfernen
        Add von Gruppen:
        1. hat eine der Gruppen direct access? -> direct access beim User eintragen, falls noch nicht da        
    """
    def info_all_dbs():
        for db in Container.objects.filter(containersystem__type=ContainerSystem.DATABASE).filter(owner=instance.owner):
            if action == 'post_remove':
                db.delete_user(instance)
            else:
                db.add_user(instance)

    if action == 'post_remove':
        for pk in pk_set:
            group = Group.objects.get(pk=pk)
            if len(group.permissions.filter(codename=PERMISSION_DIRECT_ACCESS)) > 0:
                #               print(instance.username, action, group, PERMISSION_DIRECT_ACCESS)
                if not instance.has_permission(PERMISSION_DIRECT_ACCESS):
                    #                   db_logger.info(f"User {instance} - remove {PERMISSION_DIRECT_ACCESS}")
                    info_all_dbs()
                break
    elif action == 'post_add':
        for pk in pk_set:
            group = Group.objects.get(pk=pk)
            if len(group.permissions.filter(codename=PERMISSION_DIRECT_ACCESS)) > 0:
                #               print(instance.username, action, group, PERMISSION_DIRECT_ACCESS)
                #               db_logger.info(f"User {instance} - add {PERMISSION_DIRECT_ACCESS}")
                info_all_dbs()
                break


"""
Tipp für Filter

from django.contrib.auth.models import User
from django.db.models import Q

def users_with_perm(perm_name):
    return User.objects.filter(
        Q(is_superuser=True) |
        Q(user_permissions__codename=perm_name) |
        Q(groups__permissions__codename=perm_name)).distinct()


queryset = users_with_perm('blogger')
"""
