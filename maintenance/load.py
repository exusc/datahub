from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Permission
from organization.models import *
from django.utils.translation import gettext_lazy as _
from datetime import datetime


class EnvironmentLoader():

    @classmethod
    def load(cls, request) -> str:
        """ Laden der Standard RTEs """
        def create(key, title, desc, natproc='', awlib='AW'):
            obj = Environment(
                owner=Owner.hub(), key=key, title=title, desc=desc,
                hostname='Q1.SYSTEMZ.ABRAXAS-ITS.CH', username='XXX', password='XXX',
                natproc=natproc, awlib=awlib,
                ctime=datetime.now(), cuser=request.user,
            )
            obj.save()

        create('PR', 'Prod', 'Produktion', natproc='NATAWPR')
        create('EN', 'Entw', 'Entwicklung', natproc='NATAWTE', awlib='AWE')
        create('T5', 'T5', 'Produktions-Test', natproc='NATAWTEP')
        create('TE', 'Test', 'Test', natproc='NATAWTE', awlib='AWE')
        create('AB', 'Abna', 'Abnahme', natproc='NATAWNAP')
        create('FU', 'FU', 'Fusion', natproc='NATAWT19')
        create('NK', 'NK', 'Neukunden', natproc='NATAWT12', )
        create('P9', 'PrTe', 'Produktion Tessin', natproc='NATAWP9', )
        create('TT', 'TT', 'Produktionstest Tessin', natproc='NATAWTIT', )
        create('PK', 'PrKS', 'KStA Produktion', natproc='NATAWPK', )
        return _('Environments successfully loaded')


class OwnerLoader():
    def load(self, request) -> str:
        def create(key, desc, text=None):
            obj = Owner(key=key, desc=desc, text=text,
                        ctime=datetime.now(), cuser=request.user,)
            obj.owner = obj
            obj.save()

        create('ABX', 'Abraxas',
               'Abraxas can take ownership of internal objects (databases, test applications etc.)')
        create('IGS', 'IGS gmbh',)
        create('SVA-SG', 'SVA Sankt Gallen',)
        create('SVA-ZH', 'SVA Zürich',)
        return _('Owners successfully loaded')


class ApplicationLoader():
    def load(self, request) -> str:
        """ Laden der Standard-Applikationen """
        def create(owner_key, key, desc, l1, l2=None, l3=None, l4=None):

            obj = Application(key=key,
                              owner=Owner.objects.get(key=owner_key),
                              desc=desc,
                              business_unit_1=l1,
                              business_unit_2=l2,
                              business_unit_3=l3,
                              business_unit_4=l4,
                              ctime=datetime.now(),
                              cuser=request.user,
                              # pds_vorlauf=f'TEST.US.JOBFRAMES.{key}.VORLAUF',
                              # pds_nachlauf=f'TEST.US.JOBFRAMES.{key}.NACHLAUF',
                              )
            obj.save()
        create('ABX', 'HUB', 'Steuerung der DATA-Hub-Security', 'Owner',)
        create('ABX', 'SVA', 'Applikation für alle SVAs', 'Owner',)
        create('ABX', 'AW', 'Auswertung', 'Level_1',
               'Level_2', 'Level_3', 'Level_4',)
        create('ABX', 'EK', 'Einwohnerkontrolle', 'Kunde', 'Teilnehmer',)
        create('ABX', 'FD', 'Fakturierung Debitoren',
               'Kunde', 'Teilnehmer', 'Fakturastelle',)
        create('ABX', 'SN', 'Steuern', 'Kunde', 'Teilnehmer',)
        create('ABX', 'WE', 'Wasser, Elektrizität und Gas',
               'Kunde', 'Teilnehmer',)
        create('ABX', 'ZB', 'Zugriffsberechtigung', 'Kunde', 'Teilnehmer',)
        create('ABX', 'ZP', 'Züri Primo', 'Kunde', 'Teilnehmer',)
        create('SVA-SG', 'SVA-SG-LZ',
               'SVA Sankt Gallen System L&Z', 'Team', 'Group',)
        create('SVA-SG', 'SVA-SG-BZ', 'SVA Sankt Gallen System B&Z', 'Tenant',)
        create('SVA-ZH', 'SVA-ZH',
               'Application for all Source Systems', 'Department',)
        return _('Applications successfully loaded')


class AreaLoader():
    def load(self, request) -> str:
        """ Laden der Sample Areas """
        def create(app_key, key, desc, db_key, fs_key):
            application = Application.objects.get(key=app_key)
            database = Container.objects.get(key=db_key)
            filestorage = Container.objects.get(key=fs_key)
            obj = Area(key=key, owner=application.owner,
                       application=application,
                       desc=desc, database=database, filestorage=filestorage,
                       ctime=datetime.now(),
                       cuser=request.user,
                       )
            obj.save()
        create('FD', 'RD', 'Raw Data', db_key='DAT', fs_key='MinIO')
        create('SN', 'RD', 'Raw Data', db_key='DAT', fs_key='MinIO')
        create('SVA-SG-BZ', 'RD', 'Raw Data',
               db_key='STA-SVA-SG', fs_key='FS-ABX')
        create('SVA-SG-LZ', 'RD', 'Raw Data',
               db_key='STA-SVA-SG', fs_key='FS-ABX')
        create('SVA-SG-LZ', 'BD', 'Business Data',
               db_key='STA-SVA-SG', fs_key='MinIO')
        create('SVA-SG-LZ', 'TEST', 'Test Environment',
               db_key='DAT', fs_key='FS-ABX')
        create('SVA-ZH', 'BD', 'BZ und LZ are joined here',
               db_key='STA-SVA-ZH-BD', fs_key='MinIO Zürich')
        create('SVA-ZH', 'RD_BZ', 'Raw Data BZ',
               db_key='STA-SVA-ZH-BZ', fs_key='MinIO Zürich')
        create('SVA-ZH', 'RD_LZ', 'Raw Data LZ',
               db_key='STA-SVA-ZH-LZ', fs_key='MinIO Zürich')
        return _('Areas successfully loaded')


class ScopeLoader():
    def load(self, request) -> str:
        """ Laden der Sample Scopes """
        def create(app_key, l1, l2=None, l3=None, team=None, desc=None, org_scope=None, app_scope=None, type='S'):
            application = Application.objects.get(key=app_key)
            obj = Scope(owner=application.owner,
                        type=type,
                        business_unit_1=l1,
                        business_unit_2=l2,
                        business_unit_3=l3,
                        team=team,
                        application=application,
                        desc=desc,
                        org_scope=org_scope,
                        app_scope=app_scope,
                        ctime=datetime.now(),
                        cuser=request.user,
                        )
            obj.clean()
            obj.save()
            return obj
        create('FD', 'KT', 'FD', '302')
        create('HUB', '*', desc='Berechtigung für alle Owner im DATA-Hub')
        create('HUB', 'ABX')
        create('HUB', 'IGS')
        create('HUB', 'SVA-SG')
        create('HUB', 'SVA-ZH')
        app_scope = create('SVA', '*', team='PROD', desc='Standard Templates for all SVAs', type='A')
        org_scope = create('SVA-ZH', '*', team='PROD', desc='Productive Templates for all Departments', type='O')
        create('SVA-ZH', '*', team='TEST', desc='Used to test Reports', app_scope=app_scope)
        create('SVA-ZH', '*', desc='Access to all Data', org_scope=org_scope, app_scope=app_scope)
        create('SVA-ZH', 'EK', desc='Team Einkauf', org_scope=org_scope, app_scope=app_scope)
        org_scope = create('SVA-SG-LZ', 'MKT', '*', team= 'TEMPLATES', desc='Templates for all marketing groups', type='O')
        create('SVA-SG-LZ', 'MKT', 'GP1', desc='Team Marketing - Group 1', org_scope=org_scope, app_scope=app_scope)
        create('SVA-SG-LZ', 'MKT', 'GP2', desc='Team Marketing - Group 2', org_scope=org_scope, app_scope=app_scope)
        create('SVA-SG-BZ', '*', desc='All Tenants', app_scope=app_scope)
        create('SVA-SG-BZ', 'T001', desc='Tenant 001', app_scope=app_scope)
        create('SVA-SG-BZ', 'T002', desc='Tenant 002', app_scope=app_scope)
        return _('Scopes successfully loaded')


class UserLoader():
    def load(self, request) -> str:
        def create(owner_key, username, first_name, last_name, is_staff=False, is_superuser=False):
            password = User.objects.get(username='sys').password
            user = User(username=username, first_name=first_name, last_name=last_name,
                        password=password, is_staff=is_staff, is_superuser=is_superuser,
                        owner=Owner.objects.get(key=owner_key)
                        )
            user.save()
        create('ABX', 'AXKTO', 'Tamás', 'Kovács',
               is_staff=True, is_superuser=True)
        create('ABX', 'EXUSC', 'Ulrich', 'Schoppe', is_staff=True)
        create('IGS', 'IGMSC', 'Matthias', 'Schneider',  is_staff=True)
        create('SVA-SG', 'SGMSC', 'Marcel', 'Scheiwiller', )
        create('SVA-ZH', 'ZHDUT', 'Diego', 'Utzinger', is_staff=True)
        create('SVA-ZH', 'ZHADM', 'Admin', 'Zürich',  is_staff=True)

        return _('Users successfully loaded')


class RoleLoader():
    # https://testdriven.io/blog/django-permissions/
    def load(self, request) -> str:
        def create(name, maintain=[], view_only=[]):
            group = Group(name=name, owner=Owner.objects.get(key='ABX'))
            group.save()
            for type in maintain:
                content_type = ContentType.objects.get_for_model(type)
                for perm in Permission.objects.filter(content_type=content_type):
                    if not type in view_only or perm.codename.startswith('view_'):
                        group.permissions.add(perm)
            for type in view_only:
                content_type = ContentType.objects.get_for_model(type)
                for perm in Permission.objects.filter(content_type=content_type):
                    if perm.codename.startswith('view_'):
                        group.permissions.add(perm)

            group.save()
        create('Application Admin', maintain=[
               Application, Area, Scope], view_only=[Owner])
        create('DB Admin', maintain=[ContainerType, Container])
        create('Direct Access')
        create('Report Ordering')
        create('Report Creator', maintain=[Container])
        create('User Admin', maintain=[User], view_only=[Owner, Group])
        return _('Groups successfully loaded')


class ContainerTypeLoader():

    def load(self, request) -> str:
        def create(key, desc, type):
            obj = ContainerType(
                owner=Owner.hub(), key=key, desc=desc, type=type,
                ctime=datetime.now(), cuser=request.user,
            )
            obj.save()

        create('Clickhouse', 'For Testing', ContainerType.DATABASE)
        create('PostGres', 'Standard DB', ContainerType.DATABASE)
        create('Filesystem', 'Test', ContainerType.FILESTORAGE)
        create('MinIO', 'Standard for Files', ContainerType.FILESTORAGE)
        return _('ContainerTypes successfully loaded')


class ContainerLoader():

    def load(self, request) -> str:
        def create(owner_key, key, desc, type, connection=None):
            obj = Container(owner=Owner.objects.get(key=owner_key),
                            key=key, desc=desc, connection=connection,
                            containertype=ContainerType.objects.get(key=type),
                            ctime=datetime.now(), cuser=request.user,
                            )
            obj.save()

        create('ABX', 'DAT', 'Default DB for multiple Clients',
               'PostGres', 'sta.db.dat.abraxas-apis.ch')
        create('ABX', 'FS-ABX', 'Filesystem for all Clients', 'Filesystem',
               'S:\SOE\Querschnitt-Services\Data Science\DATA-Hub')
        create('ABX', 'MinIO', 'Standard MinIO for all Clients', 'MinIO',)
        create('SVA-ZH', 'MinIO Zürich', 'Alle Files of Zürich', 'MinIO',)
        create('SVA-SG', 'STA-SVA-SG', 'DB for all SG data',
               'PostGres', 'sta.db.sva-sg.abraxas-apis.ch')
        create('SVA-ZH', 'STA-SVA-ZH-BZ', 'Only BZ data for Zürich',
               'PostGres', 'sta.db.sva-zh-bz.abraxas-apis.ch')
        create('SVA-ZH', 'STA-SVA-ZH-LZ', 'Only LZ data for Zürich',
               'PostGres', 'sta.db.sva-zh-lz.abraxas-apis.ch')
        create('SVA-ZH', 'STA-SVA-ZH-BD',
               'Business Data (BZ and LZ) - High-Performance', 'Clickhouse', )
        return _('Container successfully loaded')
