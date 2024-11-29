from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Permission
from organization.models import *
from django.utils.translation import gettext_lazy as _, ngettext
from django.utils import timezone
from datetime import datetime
from datetime import timezone as timezone2

from os import path
import csv
import json


AW_DATA_DIR = r'C:\en\abx\data\aw\pr_2024-06-11'
AW_FILE_CLIENT = 'EXKDE.csv'
AW_FILE070 = 'ex070.csv'
AW_CSV_TIMESTR = r'%d.%m.%Y %H:%M:%S'


def decode(str):
    """
    Die Files liegen in VRSG-Codepage vor und werden normalerweise im Filetransfer-Dialog umgesetzt.
    Da in diesem Fall dei Daten mit WS_ftp geholt wurden, müssen die Werte nachträglich umgesetzt werden.
    """
    result = str
    result = result.replace('€', 'ä').replace('#', 'Ä')
    result = result.replace('¾', 'ö').replace('@', 'Ö')
    result = result.replace('õ', 'ü').replace('$', 'Ü')

    result = result.replace('¤', '#').replace('ó', '@')   # .replace('–','$')
    result = result.replace('|', '!')
    return result


def strpdate(x):
    """ Returns time-field from date-string """
    return datetime.strptime(x + ' 11:00:00', AW_CSV_TIMESTR).replace(tzinfo=timezone2.utc)


class EnvironmentLoader():

    @classmethod
    def load(cls, request) -> str:
        """ Laden der Standard RTEs """
        def create(key, title, desc, natproc='', awlib='AW'):
            obj = Environment(
                owner=Owner.hub(), key=key, title=title, desc=desc,
                hostname='Q1.SYSTEMZ.ABRAXAS-ITS.CH', username='XXX', password='XXX',
                natproc=natproc, awlib=awlib,
                ctime=timezone.now(), cuser=request.user,
            )
            try:
                obj.save()
            except:
                pass

        create('PR', 'PRD', 'Produktion', natproc='NATAWPR')
        create('EN', 'STA', 'Entwicklung', natproc='NATAWTE', awlib='AWE')
        create('SE', 'SE', 'System Entwicklung', natproc='NATAWTE', awlib='AWSE')
        create('T5', 'T5', 'Produktions-Test', natproc='NATAWTEP')
        create('TE', 'Test', 'Test', natproc='NATAWTE', awlib='AWE')
        create('AB', 'UAT', 'Abnahme', natproc='NATAWNAP')
        create('FU', 'FU', 'Fusion', natproc='NATAWT19')
        create('NK', 'NK', 'Neukunden', natproc='NATAWT12', )
        create('P9', 'PRD TE', 'Produktion Tessin', natproc='NATAWP9', )
        create('TT', 'TT', 'Produktionstest Tessin', natproc='NATAWTIT', )
        create('PK', 'PRD KStA', 'KStA Produktion', natproc='NATAWPK', )
        create('T3', 'T3', 'Übernahme Neukunden', natproc='NATAWPK', )
        create('I1', 'I1', 'Integrationstest 1', natproc='NATAWT3', )
        create('I2', 'I2', 'Integrationstest 1', natproc='NATAWT22', )
        create('I3', 'I3', 'Integrationstest 1', natproc='NATAWT23', )
        create('I4', 'I4', 'Integrationstest 1', natproc='NATAWT24', )
        create('J8', 'J8', 'ACE Migration PROD', natproc='NATAWDUM', )
        create('J9', 'J9', 'ACE Migration PROD TI', natproc='NATAWDUM', )
        return _('Environments successfully loaded')


class OwnerLoader():

    def load(self, request) -> str:
        def create(key, desc, text=None):
            obj = Owner(key=key, desc=desc, text=text,
                        ctime=timezone.now(), cuser=request.user,)
            obj.owner = obj
            try:
                obj.save()
            except:
                pass

        create('ABX', 'Abraxas',
               'Abraxas can take ownership of internal objects (databases, test applications etc.)')
        create('IGS', 'IGS gmbh',)
        create('SVA-SG', 'SVA Sankt Gallen',)
        create('SVA-ZH', 'SVA Zürich',)
        return _(f'4 Owners successfully loaded')

        abx = Owner.objects.get(key='ABX')
        filename = path.join(AW_DATA_DIR, AW_FILE_CLIENT)
        owners = []
        filtered = 0
        with open(filename, 'r') as file:
            reader = csv.DictReader(file, delimiter=";")
            for row in reader:
                if len(row['KUNDENNUMMER']) > 0:
                    obj = Owner(key=row['KUNDENABKUERZUNG'],
                                desc=decode(row['KURZBEZEICHNUNG']),
                                nr=row['KUNDENNUMMER'],
                                kanton=row['KANTON'],
                                ctime=strpdate(row['MUTATIONSDATUM']),
                                cuser=row['MUTATIONS_ID'],
                                utime=strpdate(row['MUTATIONSDATUM']),
                                uuser=row['MUTATIONS_ID'],
                                owner=abx,
                                )
                    filtered += 1
                    owners.append(obj)
                if filtered >= 10:
                    pass
        try:
            Owner.objects.bulk_create(owners)
        except:
            pass
        return _(f'{len(owners)} Owners successfully loaded')

    def delete(self, request) -> str:
        count = 0
        for owner in Owner.objects.all():
            try:
                owner.delete()
                count += 1
            except:
                pass
        return _(f'{count} Owners successfully deleted')


class ApplicationLoader():
    def load(self, request) -> str:
        """ Laden der Standard-Applikationen """
        def create(owner_key, key, desc, l1=None, l2=None, l3=None, l4=None, active=True):

            obj = Application(key=key,
                              owner=Owner.objects.get(key=owner_key),
                              desc=desc,
                              bu1_type=l1,
                              bu2_type=l2,
                              bu3_type=l3,
                              bu4_type=l4,
                              ctime=timezone.now(),
                              cuser=request.user,
                              active=active
                              # pds_vorlauf=f'TEST.US.JOBFRAMES.{key}.VORLAUF',
                              # pds_nachlauf=f'TEST.US.JOBFRAMES.{key}.NACHLAUF',
                              )
            try:
                obj.save()
            except:
                pass
        create('ABX', 'taxa', 'Taxa (PoC)', 'context_key')
        create('ABX', 'HUB', 'Steuerung der DATA-Hub-Security', 'Owner')
        create('ABX', 'SVA', 'Applikation für alle SVAs', 'Owner',)
        create('ABX', 'AW', 'Auswertung', 'Level_1',
               'Level_2', 'Level_3', 'Level_4', active=False)
        create('ABX', 'EK', 'Einwohnerkontrolle', 'Kunde', 'Teilnehmer', active=False)
        create('ABX', 'FD', 'Fakturierung Debitoren',
               'Kunde', 'Teilnehmer', 'Fakturastelle', active=False)
        create('ABX', 'SN', 'Steuern', 'Kunde', 'Teilnehmer', active=False)
        create('ABX', 'WE', 'Wasser, Elektrizität und Gas',
               'Kunde', 'Teilnehmer', active=False)
        create('ABX', 'ZB', 'Zugriffsberechtigung', 'Kunde', 'Teilnehmer', active=False)
        create('ABX', 'ZP', 'Züri Primo', 'Kunde', 'Teilnehmer', active=False)
        create('ABX', 'dmo', 'Demo', )
        create('IGS', 'igs', 'Data of SVA Zürich', )
        create('SVA-SG', 'sva-sg-bz', 'SVA Sankt Gallen System B&Z', 'Tenant',)
        create('SVA-SG', 'sva-sg-elar', 'Elar Data for Use Cases')
        create('SVA-SG', 'sva-sg-lz',
               'SVA Sankt Gallen System L&Z', 'Team', 'Group',)
        create('SVA-ZH', 'sva-zh-bz', 'SVA Zürich System B&Z', )
        create('SVA-ZH', 'sva-zh-lz', 'SVA Zürich System L&Z', 'Department',)
        return _('Applications successfully loaded')


class AreaLoader():
    def load(self, request) -> str:
        """ Laden der Sample Areas """
        def create(app_key, key, desc, db_key, fs_key,st='',sv=''):
            application = Application.objects.get(key=app_key)
            database = Container.objects.get(key=db_key)
            filestorage = Container.objects.get(key=fs_key)

            obj = Area(key=key, owner=application.owner,
                       application=application,
                       desc=desc, database=database, filestorage=filestorage,
                       schematables=st,
                       schemaviews=sv,
                       ctime=timezone.now(),
                       cuser=request.user,
                       )
            try:
                obj.save()
            except:
                pass

        create('HUB', 'Control', 'Security des DATA-Hubs', db_key='ADABAS', fs_key='MinIO')
        create('FD', 'rd', 'Raw Data', db_key='ADABAS', fs_key='MinIO')
        create('SN', 'rd', 'Raw Data', db_key='ADABAS', fs_key='FS-ABX')
        create('dmo', 'rd' , 'Raw Data for Demo', db_key='dat', fs_key='MinIO')
        create('taxa', 'poc_rd' , 'Raw Data for Taxa PoC', db_key='dat', fs_key='MinIO')
        create('taxa', 'poc_dv' , 'Data Vault for Taxa PoC', db_key='dat', fs_key='MinIO', st='tax_rd_base', sv='tax_rd')
        create('igs', 'rd-zh', 'Raw Data',db_key='sta-igs', fs_key='MinIO Zürich', st='igs_zh_rd')
        create('sva-sg-bz', 'rd', 'Raw Data',db_key='sta-sva-sg', fs_key='MinIO', st='bz_bzcore_rd')
        create('sva-sg-elar', 'rd', 'Raw Data',db_key='sta-sva-sg', fs_key='MinIO', st='elar_rd')
        create('sva-sg-lz', 'ipv-rd', 'Raw Data of IPV',db_key='sta-sva-sg', fs_key='MinIO', st='lz_ipv_rd')
        create('sva-sg-lz', 'vista-rd', 'Raw Data of Vista',db_key='sta-sva-sg', fs_key='MinIO', st='lz_vista_rd')
        create('sva-zh-bz', 'rd', 'Raw Data',db_key='sta-sva-zh', fs_key='MinIO Zürich', st='bz_bzcore_rd')
        create('sva-zh-lz', 'ipv-rd', 'Raw Data of IPV',db_key='sta-sva-zh', fs_key='MinIO Zürich', st='lz_ipv_rd')
        create('sva-zh-lz', 'vista-rd', 'Raw Data of Vista',db_key='sta-sva-zh', fs_key='MinIO Zürich', st='lz_vista_rd')

        return _('Areas successfully loaded')


class AreascopeLoader():
    def load(self, request) -> str:
        """ Laden der Sample Scopes """
        def create(area_key, l1, l2=None, l3=None, team=None, desc=None, org_scope=None, app_scope=None, type='S'):

            print(area_key)
            area = Area.objects.get(key=area_key)
            
            obj = Areascope(owner=area.owner,
                        type=type,
                        bu1_value=l1,
                        bu2_value=l2,
                        bu3_value=l3,
                        team=team,
                        area=area,
                        desc=desc,
                        org_scope=org_scope,
                        app_scope=app_scope,
                        ctime=timezone.now(),
                        cuser=request.user,
                        )
            try:
                obj.clean()
                obj.save()
            except:
                pass
            return obj
        # create('FD', 'KT', 'FD', '302')
        
        create('Control', '*', desc='Berechtigung für alle Owner im DATA-Hub')
        create('Control', 'ABX')
        create('Control', 'IGS')
        create('Control', 'SVA-SG')
        create('Control', 'SVA-ZH')

        app_scope = create('poc_dv', '*', team='STD',
                           desc='Standard Templates / Abraxas', type='A')
        create('poc_dv', 'GEMEINDE_STEURION', 
               desc='Steurion', app_scope=app_scope)
        create('poc_dv', 'GEMEINDE_STEURION', team='test', 
               desc='Steurion', app_scope=app_scope)
        create('poc_dv', 'GEMEINDE_ABRAXIEN', 
               desc='Abraxien', app_scope=app_scope)

        """
        app_scope = create('igs', '*', team='PROD',
                           desc='Standard Templates for all SVAs', type='A')
        org_scope = create('igs', '*', team='PROD',
                           desc='Productive Templates for all Departments', type='O')
        create('sva-zh-lz', '*', team='TEST',
               desc='Used to test Reports', app_scope=app_scope)
        create('sva-zh-lz', '*', team='PROD',
               desc='Productive Reports', app_scope=app_scope)
        create('sva-zh-lz', '*', desc='Access to all Data',
               org_scope=org_scope, app_scope=app_scope)
        create('sva-zh-lz', 'EK', desc='Team Einkauf',
               org_scope=org_scope, app_scope=app_scope)
        org_scope = create('sva-zh-lz', 'MKT', '*', team='TEMPLATES',
                           desc='Templates for all marketing groups', type='O')
        create('sva-zh-lz', 'MKT', 'GP1', desc='Team Marketing - Group 1',
               org_scope=org_scope, app_scope=app_scope)
        create('sva-zh-lz', 'MKT', 'GP2', desc='Team Marketing - Group 2',
               org_scope=org_scope, app_scope=app_scope)
        create('sva-zh-bz', '*', desc='All Tenants', app_scope=app_scope)
        create('sva-zh-bz', 'T001', desc='Tenant 001', app_scope=app_scope)
        create('sva-zh-bz', 'T002', desc='Tenant 002', app_scope=app_scope)
        """

        txt = _('Scopes successfully loaded')
        txt = self.load_aw()
        return txt

    def load_aw(self):
        return 'nix'
        applications = {}
        for application in Application.objects.all():
            applications[application.key] = application

        filename = path.join(AW_DATA_DIR, AW_FILE070)
        scopes = {}
        filtered = 0
        with open(filename, 'r') as file:
            reader = csv.DictReader(file, delimiter=";")
            for row in reader:
                if (row['SATZART'] == 'O') and (len(row['NAME']) > 1):
                    level = row['NAME'].split('_')
                    application_key = level[0]
                    application = applications[application_key]

                    scope = Scope(application=application,
                                  owner=application.owner,
                                  key=row['NAME'],
                                  hex=row['OWNER_KEY'],
                                  desc=decode(row['OWNER_BESCHREIBUNG']),
                                  type='S',
                                  # client=row['OWNER_KUNDENNUMMER'],
                                  utime=datetime.strptime(
                                      row['MUTATIONSDATUMZEIT'], AW_CSV_TIMESTR).replace(tzinfo=timezone2.utc),
                                  uuser=row['MUTATION_USER_ID'],
                                  ctime=datetime.strptime(
                                      row['MUTATIONSDATUMZEIT'], AW_CSV_TIMESTR).replace(tzinfo=timezone2.utc),
                                  cuser=row['MUTATION_USER_ID'],
                                  business_unit_1=level[1],
                                  )
                    if len(level) > 2:
                        scope.business_unit_2 = level[2]
                    if len(level) > 3:
                        scope.business_unit_3 = level[3]
                    if len(level) > 4:
                        scope.business_unit_4 = level[4]
                    if row['GLOBAL_OWNER_KZ'] == 'O':
                        scope.type = 'O'
                    if row['GLOBAL_OWNER_KZ'] == 'F':
                        scope.type = 'A'
                    if row['GLOBAL_OWNER_KZ'] == 'T':
                        scope.type = 'T'
                    scope.global_app_owner_key = row['GLOBAL_APPL_OWNER_KEY']
                    scope.global_org_owner_key = row['GLOBAL_ORG_OWNER_KEY']
                    scopes[scope.hex] = scope
                    filtered += 1

        # Scopes, die keine 'eigenen' Scopes sind speichern
        scope_list1 = []
        for scope in scopes.values():
            if not scope.type == 'S':
                scope_list1.append(scope)
        Scope.objects.bulk_create(scope_list1)

        # Scope, die 'eigene' Scopes sind, um die Template-Owner ergänzen und dann speichern
        scope_list2 = []
        for scope in scopes.values():
            if scope.type == 'S':
                scope.org_scope = scopes.get(scope.global_org_owner_key)
                scope.app_scope = scopes.get(scope.global_app_owner_key)
                scope_list2.append(scope)
                if len(scope_list2) >= 100:
                    pass
                    # break
        Scope.objects.bulk_create(scope_list2)

        return _(f'{len(scope_list1) + len(scope_list2)} Scopes loaded')

    def delete(self, request) -> str:
        """ Delete only imported scopes from AW """
        count = 0
        for scope in Scope.objects.all().filter(type='S'):
            if scope.hex:
                try:
                    scope.delete()
                    count += 1
                except:
                    pass
        for scope in Scope.objects.all():
            if scope.hex:
                try:
                    scope.delete()
                    count += 1
                except:
                    pass
        return _(f'{count} Scopes successfully deleted')


class UserLoader():
    def load(self, request) -> str:
        def create(owner_key, username, first_name, last_name, is_staff=False, is_superuser=False):
            password = User.objects.get(username='sys').password
            user = User(username=username, first_name=first_name, last_name=last_name,
                        password=password, is_staff=is_staff, is_superuser=is_superuser,
                        owner=Owner.objects.get(key=owner_key)
                        )
            try:
                user.save()
            except:
                return None
            return user
        create('ABX', 'AXKTO', 'Tamás', 'Kovács',
               is_staff=True, is_superuser=True)
        user = create('ABX', 'AXUSC03', 'Ulrich', 'Schoppe', is_staff=True)
        if user:
            user.groups.add(Group.objects.get(name='Report Ordering'))
            user.groups.add(Group.objects.get(name='Report Creator'))
            #user.scopes.add(Scope.objects.get(key='TAXA_GEMEINDE_ABRAXIEN'))
            #user.scopes.add(Scope.objects.get(key='TAXA_GEMEINDE_STEURION'))
            #user.scopes.add(Scope.objects.get(key='TAXA_GEMEINDE_STEURION/TEST'))

        user = create('IGS', 'IGMSC', 'Matthias', 'Schneider',  is_staff=True)
        if user:
            user.groups.add(Group.objects.get(name='User Admin'))
            #user.scopes.add(Scope.objects.get(key='HUB_IGS'))
            #user.scopes.add(Scope.objects.get(key='HUB_SVA-SG'))
            #user.scopes.add(Scope.objects.get(key='HUB_SVA-ZH'))

        user = create('SVA-SG', 'SGMSC', 'Marcel', 'Scheiwiller', )
        if user:
            user.groups.add(Group.objects.get(name='Report Ordering'))
            user.groups.add(Group.objects.get(name='Report Creator'))
            user.scopes.add(Scope.objects.get(key='HUB_SVA-SG'))
            #user.scopes.add(Scope.objects.get(key='SVA-SG-LZ_MKT_GP1'))
            #user.scopes.add(Scope.objects.get(key='SVA-SG-LZ_MKT_GP2'))
            #user.scopes.add(Scope.objects.get(key='SVA-SG-BZ_*'))

        user = create('SVA-ZH', 'ZHDUT', 'Diego', 'Utzinger', is_staff=True)
        if user:
            user.groups.add(Group.objects.get(name='Application Admin'))
            user.groups.add(Group.objects.get(name='Direct Access'))
            user.groups.add(Group.objects.get(name='User Admin'))
            user.groups.add(Group.objects.get(name='Report Ordering'))
            user.groups.add(Group.objects.get(name='Report Creator'))
            user.scopes.add(Scope.objects.get(key='HUB_SVA-ZH'))
            #user.scopes.add(Scope.objects.get(key='SVA-ZH-BZ_*'))
            #user.scopes.add(Scope.objects.get(key='SVA-ZH-LZ_*/TEST'))
            #user.scopes.add(Scope.objects.get(key='SVA-ZH-LZ_*/PROD'))

        user = create('SVA-ZH', 'ZHADM', 'Admin', 'Zürich',  is_staff=True)
        if user:
            user.groups.add(Group.objects.get(name='Application Admin'))
            user.groups.add(Group.objects.get(name='DB Admin'))
            user.groups.add(Group.objects.get(name='User Admin'))
            user.scopes.add(Areascope.objects.get(key='HUB_Control/SVA-ZH'))

        sys = User.objects.get(username='sys')
        sys.first_name = 'Super'
        sys.last_name = 'User'
        sys.save()

        return _('Users successfully loaded')


class RoleLoader():
    # https://testdriven.io/blog/django-permissions/
    def load(self, request) -> str:
        def create(name, maintain=[], view_only=[], permissions=[]):
            group = Group(name=name, owner=Owner.objects.get(key='ABX'))
            try:
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
                for permission in permissions:
                    perm = Permission.objects.get(codename=permission)
                    if perm:
                        group.permissions.add(perm)
                group.save()
            except:
                pass
                
        create('Application Admin', maintain=[
               Application, Area, Scope], view_only=[Owner])
        create('DB Admin', maintain=[ContainerSystem, Container])
        create('Direct Access', permissions=[PERMISSION_DIRECT_ACCESS])
        create('Report Ordering', permissions=[])
        create('Report Creator', permissions=[PERMISSION_UPLOAD_TEMPLATES, PERMISSION_DOWNLOAD_TEMPLATES])
        create('User Admin', maintain=[User], view_only=[Owner, Group])
        return _('Groups successfully loaded')


class ContainerSystemLoader():

    def load(self, request) -> str:
        def create(key, desc, type, connection={}):
            obj = ContainerSystem(
                owner=Owner.hub(), key=key, desc=desc, type=type,
                ctime=timezone.now(), cuser=request.user,
                connection=connection,
            )
            try:
                obj.save()
            except:
                pass


        create('Clickhouse', 'For Testing', ContainerSystem.DATABASE)
        create('PostGreSQL', 'Standard DB', ContainerSystem.DATABASE, {"ENGINE" : "django.db.backends.postgresql"})
        create('SqlLite', 'Django DB', ContainerSystem.DATABASE, {"ENGINE": "django.db.backends.sqlite3"})
        create('ACE_TE', 'ACE Server for MF ADABAS - Test', ContainerSystem.DATABASE, {"HOST": "cnxJDBC-TEST.systemz.abraxas-its.ch", "PORT": "6000", "cdd": "rte_TEST"})
        create('Filesystem', 'Test', ContainerSystem.FILESTORAGE)
        create('MinIO', 'Standard for Files', ContainerSystem.FILESTORAGE)
        return _('ContainerSystems successfully loaded')


class ContainerLoader():

    def load(self, request) -> str:
        def create(owner_key, key, desc, type, connection={}):
            obj = Container(owner=Owner.objects.get(key=owner_key),
                            key=key, desc=desc, 
                            containersystem=ContainerSystem.objects.get(key=type),
                            connection=connection,
                            ctime=timezone.now(), cuser=request.user,
                            )
            try:
                obj.save()
            except:
                pass

        pg_sta = {}
        pg_sta['NAME'] = 'sta_dat'
        pg_sta['HOST'] = 'sta.db.dat.abraxas-apis.ch'
        pg_sta['PORT'] = '5432'
        # pg_sta['OPTIONS'] = {'sslmode': 'require',}


        create('ABX', 'dat', 'Default DB for multiple Clients',
               'PostGreSQL', pg_sta)
        create('ABX', 'FS-ABX', 'Filesystem for all Clients', 'Filesystem',)


        pg_sta['NAME'] = 'sta_igs'
        create('SVA-SG', 'sta-igs', 'DB for all SVAs',
               'PostGreSQL', pg_sta)

        pg_sta['NAME'] = 'sta_sva_sg'
        create('SVA-SG', 'sta-sva-sg', 'DB for all St.Gallen Data',
               'PostGreSQL', pg_sta)

        pg_sta['NAME'] = 'sta_sva_zh'
        create('SVA-ZH', 'sta-sva-zh', 'DB for all Zürich Data',
               'PostGreSQL', pg_sta)
        
        create('SVA-ZH', 'sta-sva-zh-bd',
               'Business Data (BZ and LZ) - High-Performance', 'Clickhouse', )

        adabas = {}
        adabas['NAME'] = 'ADABAS'
        create('ABX', 'ADABAS', 'ADABAS via ACE',
               'ACE_TE', adabas)

        minio = {}
        minio['bucket'] = 'xxx.yyy.zzz.abraxas'
        create('ABX', 'MinIO', 'Standard MinIO for all Clients', 'MinIO', minio)

        minio['bucket'] = 'xxx.yyy.zzz.sva-zh'
        create('SVA-ZH', 'MinIO Zürich', 'Standard MinIO for SVA Zürich', 'MinIO', minio)

        create('ABX', 'Django', 'Test Lokal', 'SqlLite', {'NAME' : r'C:\en\abx\datahub\data.sqlite3'})

        return _('Container successfully loaded')
