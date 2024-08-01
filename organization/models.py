from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models, connections
from django.contrib.auth.models import AbstractUser, Group
from datahub.settings import LANGUAGES, HUB_OWNER_KEY, HUB_APPLICATION_KEY, DATABASES
from django.utils.translation import gettext as _
import uuid


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

    ctime = models.DateTimeField(_('ctime'), null=True, blank=True,)
    cuser = models.CharField(_('cuser'), max_length=8, null=True, blank=True,)
    utime = models.DateTimeField(_('utime'), null=True, blank=True, )
    uuser = models.CharField(_('uuser'), max_length=8, null=True, blank=True, )

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
        ordering = ['-key']
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


class ContainerType(AbstractDatahubModel):
    """ ContainerType defines how the hub handels different activities like
        adding an area, adding an user, ...
    """
    class Meta:
        verbose_name = _("ContainerType")
        verbose_name_plural = _("ContainerTypes")

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



        TODO: implement methods add_scope, delete_scope using scripts from ContainerType


    """
    class Meta:
        verbose_name = _("Container")
        verbose_name_plural = _("Containers")
        permissions = [
            ("upload_templates", "Is allowed to upload report templates"),
            ("download_templates", "Is allowed to download report templates"),
        ]

    def __init__(self, *args, **kwargs):
        self.__schemas = None
        super().__init__(*args, **kwargs)

    owner = models.ForeignKey(
        to=Owner, on_delete=models.PROTECT, related_name='+',)
    key = models.CharField(_('key'), max_length=20, unique=True,)
    containertype = models.ForeignKey(
        to=ContainerType, on_delete=models.PROTECT)
    connection = models.JSONField(_('Connection'), null=True,
                                  blank=True, help_text=_("To establish connection to container"))

    def add_scope(self, area, scope):
        print(f'Container {str(self):15} : "add_scope"  Area: {area.key:10}  Application: {area.application.key:10}  Scope: {scope.key}  Connection:{self.connection}')
        print(self.containertype.scope_add)

    def add_area(self, area):
        print(
            f'Container {str(self):15} : "add_area "  Area: {area.key:10}  Application: {area.application.key:10}  Connection:{self.connection}')

    @property
    def __name(self):
        """ Returns a string used as identifier for connection """
        return str(self.id)

    def __add_to_settings(self):
        if not self.containertype.type == 'DB':
            raise Exception(f'This container ({self.key}) is not type database')

        """ Adds the database to the settings.DATABASES, if it not exists
        """
        if not DATABASES.get(self.__name):
            # Create database dynamic based on 'default'
            db = DATABASES['default'].copy()
            # db['NAME'] = r'C:\en\abx\datahub\db-dynamic.sqlite3'
            # https://www2.sqlite.org/cvstrac/wiki?p=InformationSchema
            # Set defaults dependent of containetype
            db.update(self.containertype.connection)
            db.update(self.connection)
            # Hardcoded Defaults
            db['USER'] = 'postgres'
            db['PASSWORD'] = '.Paraolimpia1235'
            DATABASES[self.__name] = db
            """
            db['HOST'] = 'sta.db.dat.abraxas-apis.ch'
            db['USER'] = 'postgres'
            db['PASSWORD'] = 'xxx'
            db['OPTIONS'] = {'sslmode': 'require',}
            """

    def exec_sql(self,sql_string):
        if not self.containertype.type == 'DB':
            raise Exception(f'This container ({self.key}) is not type database')
        self.__add_to_settings()
        with connections[self.__name].cursor() as cursor:
            cursor.execute(sql_string)
            rows = cursor.fetchall()
            return [row[0] for row in rows]
            # columns = [col[0] for col in cursor.description]
            # return [dict(zip(columns, row)) for row in rows]

    def schemas(self):
        if not self.__schemas:
            self.__schemas = self.exec_sql("select nspname as schema from pg_catalog.pg_namespace where not nspowner = 10")
        return self.__schemas


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

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        self.owner = self.application.owner

        print('-'*80)
        # Implement Area and Scopes in Container
        self.database.add_area(self)
        for scope in self.application.scope_set.all():
            self.database.add_scope(self, scope)
        self.filestorage.add_area(self)
        for scope in self.application.scope_set.all():
            self.filestorage.add_scope(self, scope)
        print('-'*80)

        super().save(force_insert, force_update, using, update_fields)

    def schema(self):
        return f'{self.application.key}_{self.key}_base'


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

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):

        super().save(force_insert=force_insert, force_update=force_update,
                     using=using, update_fields=update_fields)
        """ While saving a scope, the scope has to be added to the container"""
        print('-'*80)
        for area in self.application.area_set.all():
            area.database.add_scope(area, self)
        for area in self.application.area_set.all():
            area.filestorage.add_scope(area, self)
        print('-'*80)


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
