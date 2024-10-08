# Generated by Django 5.0.3 on 2024-08-27 12:19

import django.contrib.auth.models
import django.contrib.auth.validators
import django.db.models.deletion
import django.utils.timezone
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Owner',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('active', models.BooleanField(default=True, help_text='Inactive object is not available for end users', verbose_name='active')),
                ('desc', models.CharField(blank=True, max_length=80, null=True, verbose_name='desc')),
                ('text', models.TextField(blank=True, null=True, verbose_name='text')),
                ('ctime', models.DateTimeField(blank=True, null=True, verbose_name='ctime')),
                ('cuser', models.CharField(blank=True, max_length=8, null=True, verbose_name='cuser')),
                ('utime', models.DateTimeField(blank=True, null=True, verbose_name='utime')),
                ('uuser', models.CharField(blank=True, max_length=8, null=True, verbose_name='uuser')),
                ('key', models.CharField(max_length=20, unique=True, verbose_name='key')),
                ('kanton', models.CharField(blank=True, max_length=2, null=True, verbose_name='kanton')),
                ('nr', models.IntegerField(blank=True, null=True, verbose_name='kundennr')),
                ('owner', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='+', to='organization.owner')),
            ],
            options={
                'verbose_name': 'Owner',
                'verbose_name_plural': 'Owners',
                'ordering': ['key'],
                'permissions': [('view_dashboard', 'Can view Dashboard')],
            },
        ),
        migrations.CreateModel(
            name='Group',
            fields=[
                ('group_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='auth.group')),
                ('owner', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='organization.owner')),
            ],
            options={
                'verbose_name': 'Role',
                'verbose_name_plural': 'Roles',
            },
            bases=('auth.group',),
            managers=[
                ('objects', django.contrib.auth.models.GroupManager()),
            ],
        ),
        migrations.CreateModel(
            name='Environment',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('active', models.BooleanField(default=True, help_text='Inactive object is not available for end users', verbose_name='active')),
                ('desc', models.CharField(blank=True, max_length=80, null=True, verbose_name='desc')),
                ('text', models.TextField(blank=True, null=True, verbose_name='text')),
                ('ctime', models.DateTimeField(blank=True, null=True, verbose_name='ctime')),
                ('cuser', models.CharField(blank=True, max_length=8, null=True, verbose_name='cuser')),
                ('utime', models.DateTimeField(blank=True, null=True, verbose_name='utime')),
                ('uuser', models.CharField(blank=True, max_length=8, null=True, verbose_name='uuser')),
                ('key', models.CharField(blank=True, max_length=2, null=True, unique=True, verbose_name='key')),
                ('title', models.CharField(max_length=10, verbose_name='title')),
                ('hostname', models.CharField(blank=True, max_length=64, null=True, verbose_name='hostname')),
                ('username', models.CharField(blank=True, max_length=8, null=True, verbose_name='username')),
                ('password', models.CharField(blank=True, max_length=8, null=True, verbose_name='password')),
                ('ace_connect', models.CharField(blank=True, max_length=256, null=True, verbose_name='ace_connect')),
                ('natproc', models.CharField(blank=True, help_text='Used in batch job.', max_length=8, null=True, verbose_name='natproc')),
                ('awlib', models.CharField(blank=True, help_text='Used in batch job.', max_length=8, null=True, verbose_name='awlib')),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='+', to='organization.owner')),
            ],
            options={
                'verbose_name': 'Environment',
                'verbose_name_plural': 'Environments',
            },
        ),
        migrations.CreateModel(
            name='ContainerType',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('active', models.BooleanField(default=True, help_text='Inactive object is not available for end users', verbose_name='active')),
                ('desc', models.CharField(blank=True, max_length=80, null=True, verbose_name='desc')),
                ('text', models.TextField(blank=True, null=True, verbose_name='text')),
                ('ctime', models.DateTimeField(blank=True, null=True, verbose_name='ctime')),
                ('cuser', models.CharField(blank=True, max_length=8, null=True, verbose_name='cuser')),
                ('utime', models.DateTimeField(blank=True, null=True, verbose_name='utime')),
                ('uuser', models.CharField(blank=True, max_length=8, null=True, verbose_name='uuser')),
                ('key', models.CharField(max_length=20, unique=True, verbose_name='key')),
                ('type', models.CharField(choices=[('DB', 'DataBase'), ('FS', 'FileStorage')], max_length=2, verbose_name='type')),
                ('connection', models.JSONField(blank=True, help_text='Base information for connection like middleware', null=True, verbose_name='Connection')),
                ('area_add', models.TextField(blank=True, help_text='Script used to add an area to container', null=True, verbose_name='area_add')),
                ('user_add', models.TextField(blank=True, help_text='Script used to add a user to container', null=True, verbose_name='user_add')),
                ('user_del', models.TextField(blank=True, help_text='Script used to delete a user from container', null=True, verbose_name='user_del')),
                ('scope_add', models.TextField(blank=True, help_text='Script used to add a scope to container', null=True, verbose_name='scope_add')),
                ('scope_del', models.TextField(blank=True, help_text='Script used to delete a scope from container', null=True, verbose_name='scope_del')),
                ('user_to_scope', models.TextField(blank=True, help_text='Script used to link a user to a container', null=True, verbose_name='user_to_scope')),
                ('user_from_scope', models.TextField(blank=True, help_text='Script used to unlink a user from a container', null=True, verbose_name='user_from_scope')),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='+', to='organization.owner')),
            ],
            options={
                'verbose_name': 'ContainerType',
                'verbose_name_plural': 'ContainerTypes',
            },
        ),
        migrations.CreateModel(
            name='Container',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('active', models.BooleanField(default=True, help_text='Inactive object is not available for end users', verbose_name='active')),
                ('desc', models.CharField(blank=True, max_length=80, null=True, verbose_name='desc')),
                ('text', models.TextField(blank=True, null=True, verbose_name='text')),
                ('ctime', models.DateTimeField(blank=True, null=True, verbose_name='ctime')),
                ('cuser', models.CharField(blank=True, max_length=8, null=True, verbose_name='cuser')),
                ('utime', models.DateTimeField(blank=True, null=True, verbose_name='utime')),
                ('uuser', models.CharField(blank=True, max_length=8, null=True, verbose_name='uuser')),
                ('key', models.CharField(max_length=20, unique=True, verbose_name='key')),
                ('connection', models.JSONField(blank=True, help_text='To establish connection to container', null=True, verbose_name='Connection')),
                ('containertype', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='organization.containertype')),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='+', to='organization.owner')),
            ],
            options={
                'verbose_name': 'Container',
                'verbose_name_plural': 'Containers',
                'ordering': ['key'],
                'permissions': [('upload_templates', 'Is allowed to upload report templates'), ('download_templates', 'Is allowed to download report templates')],
            },
        ),
        migrations.CreateModel(
            name='Application',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('active', models.BooleanField(default=True, help_text='Inactive object is not available for end users', verbose_name='active')),
                ('desc', models.CharField(blank=True, max_length=80, null=True, verbose_name='desc')),
                ('text', models.TextField(blank=True, null=True, verbose_name='text')),
                ('ctime', models.DateTimeField(blank=True, null=True, verbose_name='ctime')),
                ('cuser', models.CharField(blank=True, max_length=8, null=True, verbose_name='cuser')),
                ('utime', models.DateTimeField(blank=True, null=True, verbose_name='utime')),
                ('uuser', models.CharField(blank=True, max_length=8, null=True, verbose_name='uuser')),
                ('key', models.CharField(max_length=20, unique=True, verbose_name='key')),
                ('business_unit_1', models.CharField(blank=True, max_length=80, null=True, verbose_name='business_unit_1')),
                ('business_unit_2', models.CharField(blank=True, max_length=80, null=True, verbose_name='business_unit_2')),
                ('business_unit_3', models.CharField(blank=True, max_length=80, null=True, verbose_name='business_unit_3')),
                ('business_unit_4', models.CharField(blank=True, max_length=80, null=True, verbose_name='business_unit_4')),
                ('business_unit_5', models.CharField(blank=True, max_length=80, null=True, verbose_name='business_unit_5')),
                ('regex_1', models.CharField(blank=True, max_length=80, null=True, verbose_name='regex_1')),
                ('regex_2', models.CharField(blank=True, max_length=80, null=True, verbose_name='regex_2')),
                ('regex_3', models.CharField(blank=True, max_length=80, null=True, verbose_name='regex_3')),
                ('regex_4', models.CharField(blank=True, max_length=80, null=True, verbose_name='regex_4')),
                ('regex_5', models.CharField(blank=True, max_length=80, null=True, verbose_name='regex_5')),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='organization.owner')),
            ],
            options={
                'verbose_name': 'Application',
                'verbose_name_plural': 'Applications',
                'ordering': ['key'],
            },
        ),
        migrations.CreateModel(
            name='Scope',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('active', models.BooleanField(default=True, help_text='Inactive object is not available for end users', verbose_name='active')),
                ('desc', models.CharField(blank=True, max_length=80, null=True, verbose_name='desc')),
                ('text', models.TextField(blank=True, null=True, verbose_name='text')),
                ('ctime', models.DateTimeField(blank=True, null=True, verbose_name='ctime')),
                ('cuser', models.CharField(blank=True, max_length=8, null=True, verbose_name='cuser')),
                ('utime', models.DateTimeField(blank=True, null=True, verbose_name='utime')),
                ('uuser', models.CharField(blank=True, max_length=8, null=True, verbose_name='uuser')),
                ('key', models.CharField(default='tbd', max_length=80, unique=True, verbose_name='key')),
                ('hex', models.CharField(blank=True, help_text='Hex value for AW data', max_length=8, null=True, verbose_name='hex')),
                ('type', models.CharField(choices=[('S', 'Standard'), ('O', 'Org scope'), ('A', 'App scope'), ('T', 'Test scope')], default='S', help_text='Defines how scope can be used', max_length=1, verbose_name='type')),
                ('business_unit_1', models.CharField(blank=True, max_length=80, null=True, verbose_name='business_unit_1')),
                ('business_unit_2', models.CharField(blank=True, max_length=80, null=True, verbose_name='business_unit_2')),
                ('business_unit_3', models.CharField(blank=True, max_length=80, null=True, verbose_name='business_unit_3')),
                ('business_unit_4', models.CharField(blank=True, max_length=80, null=True, verbose_name='business_unit_4')),
                ('business_unit_5', models.CharField(blank=True, max_length=80, null=True, verbose_name='business_unit_5')),
                ('team', models.CharField(blank=True, max_length=80, null=True, verbose_name='team')),
                ('app_scope', models.ForeignKey(blank=True, help_text='Here are the standard templates created by Abraxas or other provider', null=True, on_delete=django.db.models.deletion.PROTECT, related_name='+', to='organization.scope')),
                ('application', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='organization.application')),
                ('org_scope', models.ForeignKey(blank=True, help_text='Here are the standard templates created by the client', null=True, on_delete=django.db.models.deletion.PROTECT, related_name='+', to='organization.scope')),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='+', to='organization.owner')),
            ],
            options={
                'verbose_name': 'Scope',
                'verbose_name_plural': 'Scopes',
            },
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('language', models.CharField(choices=[('de', 'German'), ('it', 'Italien'), ('fr', 'French'), ('en', 'English')], default='en', help_text='Language used for DATA-Hub UI', max_length=5, verbose_name='language')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
                ('owner', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='organization.owner')),
                ('scopes', models.ManyToManyField(blank=True, to='organization.scope')),
                ('use_scope', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='+', to='organization.scope')),
            ],
            options={
                'verbose_name': 'User',
                'verbose_name_plural': 'Users',
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Area',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('active', models.BooleanField(default=True, help_text='Inactive object is not available for end users', verbose_name='active')),
                ('desc', models.CharField(blank=True, max_length=80, null=True, verbose_name='desc')),
                ('text', models.TextField(blank=True, null=True, verbose_name='text')),
                ('ctime', models.DateTimeField(blank=True, null=True, verbose_name='ctime')),
                ('cuser', models.CharField(blank=True, max_length=8, null=True, verbose_name='cuser')),
                ('utime', models.DateTimeField(blank=True, null=True, verbose_name='utime')),
                ('uuser', models.CharField(blank=True, max_length=8, null=True, verbose_name='uuser')),
                ('key', models.CharField(max_length=20, verbose_name='key')),
                ('schematables', models.CharField(blank=True, help_text='Overwrite default (app.key_area.key_base)', max_length=40, null=True, verbose_name='schematables')),
                ('schemaviews', models.CharField(blank=True, help_text='Overwrite default (app.key_area.key)', max_length=40, null=True, verbose_name='schemaviews')),
                ('application', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='organization.application')),
                ('database', models.ForeignKey(help_text='To store structured data', on_delete=django.db.models.deletion.PROTECT, related_name='+', to='organization.container')),
                ('filestorage', models.ForeignKey(help_text='To store files', on_delete=django.db.models.deletion.PROTECT, related_name='+', to='organization.container')),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='+', to='organization.owner')),
            ],
            options={
                'verbose_name': 'Area',
                'verbose_name_plural': 'Areas',
                'unique_together': {('application', 'key')},
            },
        ),
    ]
