from django.db import models
from django.contrib.auth.models import AbstractUser, Group
from datahub.settings import LANGUAGES
from django.utils.translation import gettext as _
import uuid


class AbstractDatahubModel(models.Model):
    """ Default definition of all DATA-Hub objects
    """

    class Meta:
        abstract = True

    owner = models.ForeignKey(
        'Owner', on_delete=models.PROTECT, null=True, blank=True, related_name='+',)

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    desc = models.CharField(_('desc'), max_length=80, null=True, blank=True)
    text = models.TextField(_('text'), null=True, blank=True)

    ctime = models.DateTimeField(_('ctime'), null=True, blank=True,)
    cuser = models.CharField(_('cuser'), max_length=8, null=True, blank=True,)
    utime = models.DateTimeField(_('utime'), null=True, blank=True, )
    uuser = models.CharField(_('uuser'), max_length=8, null=True, blank=True, )

    def __str__(self):
        """ Field 'Key' has to be defined in derived class       
        if self.desc:
            return f'{self.key} ({self.desc})'
        """
        return f'{self.key}'


class User(AbstractUser):
    """ If a user is assigned to an owner, that person is just allowed to work with owner related objects """
    class Meta:
        verbose_name = _("User")
        verbose_name_plural = _("Users")

    owner = models.ForeignKey(
        'Owner', on_delete=models.PROTECT, null=True, blank=True,)
    scopes = models.ManyToManyField('Scope', blank=True)
    language = models.CharField(_('language'), max_length=5, choices=LANGUAGES, default='en',
                            help_text=_("Language used for DATA-Hub UI"))


class Group(Group):
    class Meta:
        verbose_name = _("Group")
        verbose_name_plural = _("Groups")

    owner = models.ForeignKey(
        'Owner', on_delete=models.PROTECT, null=True, blank=True,)


class Owner(AbstractDatahubModel):
    """ Used to assign ownership to applications and container.
        A owner might be owned by an other organization
    """
    class Meta:
        verbose_name = _("Owner")
        verbose_name_plural = _("Owners")

    key = models.CharField(_('key'), max_length=20, unique=True,)


class Application(AbstractDatahubModel):
    """ Business units are defined on application level - in this prototype its just a simple definition
        For real implementation this mut be a separate object with information about allowed values ...
    """
    class Meta:
        verbose_name = _("Application")
        verbose_name_plural = _("Applications")

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


class Area(AbstractDatahubModel):
    """ Each area belongs to an application and can have its own database and file storage"""
    class Meta:
        verbose_name = _("Area")
        verbose_name_plural = _("Areas")
        unique_together = ['application', 'key']

    key = models.CharField(_('key'), max_length=20)
    application = models.ForeignKey('Application', on_delete=models.PROTECT)
    database = models.ForeignKey(
        'Container', on_delete=models.PROTECT, related_name='+', help_text=_("To store structured data"))
    filestorage = models.ForeignKey(
        'Container', on_delete=models.PROTECT, related_name='+', help_text=_("To store files"))

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


class Scope(AbstractDatahubModel):
    """ Scopes are linked to application and used from all areas within these application """
    class Meta:
        verbose_name = _("Scope")
        verbose_name_plural = _("Scopes")

    TYPE = {
        "S": _("Standard"),
        "O": _("Org scope"),
        "A": _("App scope"),
    }

    key = models.CharField(_('key'), max_length=80, unique=True, default="tbd")
    type = models.CharField(_('type'), max_length=1, choices=TYPE, default='S',
                            help_text=_("Defines how scope can be used"))
    application = models.ForeignKey(
        'Application', on_delete=models.PROTECT, null=True, blank=True,)
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
    team = models.CharField(_('team'), max_length=80, null=True, blank=True)
    org_scope = models.ForeignKey('Scope', on_delete=models.PROTECT, null=True, blank=True, related_name='+',
                                  help_text=_("Here are the standard templates created by the client"))
    app_scope = models.ForeignKey('Scope', on_delete=models.PROTECT, null=True, blank=True, related_name='+',
                                  help_text=_("Here are the standard templates created by Abraxas or other provider"))

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        
        self.owner = self.application.owner
        """ Creates the key based on the BUs
        """
        self.key = f'{self.application.key.upper()}_{self.business_unit_1.upper()}'
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

        # Implement Scope in Container
        print('-'*80)
        for area in self.application.area_set.all():
            area.database.add_scope(area, self)
        for area in self.application.area_set.all():
            area.filestorage.add_scope(area, self)
        print('-'*80)

        super().save(force_insert, force_update, using, update_fields)


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

    key = models.CharField(_('key'), max_length=20, unique=True,)
    containertype = models.ForeignKey(
        'ContainerType', on_delete=models.PROTECT)
    connection = models.TextField(_('Connection'), max_length=200, null=True,
                                  blank=True, help_text=_("Script to establish connection to container"))

    def add_scope(self, area, scope ):
        print(f'Container {str(self):15} : "add_scope"  Area: {area.key:10}  Application: {area.application.key:10}  Scope: {scope.key}  Connection:{self.connection}')
        print (self.containertype.scope_add)

    def add_area(self, area):
        print(f'Container {str(self):15} : "add_area "  Area: {area.key:10}  Application: {area.application.key:10}  Connection:{self.connection}')


class ContainerType(AbstractDatahubModel):
    """ ContainerType defines how the hub handels different activities like
        adding an area, adding an user, ...
    """
    class Meta:
        verbose_name = _("ContainerType")
        verbose_name_plural = _("ContainerTypes")

    TYPE = {
        "DB": _("DataBase"),
        "FS": _("FileStorage"),
    }

    key = models.CharField(_('key'), max_length=20, unique=True,)
    type = models.CharField(_('type'), max_length=2, choices=TYPE)
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
