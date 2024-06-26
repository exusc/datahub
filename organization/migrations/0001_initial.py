# Generated by Django 5.0.3 on 2024-06-21 10:11

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
            name='ContainerType',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('desc', models.CharField(blank=True, max_length=80, null=True, verbose_name='desc')),
                ('text', models.TextField(blank=True, null=True, verbose_name='text')),
                ('ctime', models.DateTimeField(blank=True, null=True, verbose_name='ctime')),
                ('cuser', models.CharField(blank=True, max_length=8, null=True, verbose_name='cuser')),
                ('utime', models.DateTimeField(blank=True, null=True, verbose_name='utime')),
                ('uuser', models.CharField(blank=True, max_length=8, null=True, verbose_name='uuser')),
                ('key', models.CharField(max_length=20, unique=True, verbose_name='key')),
                ('type', models.CharField(choices=[('DB', 'DataBase'), ('FS', 'FileStorage')], max_length=2, verbose_name='type')),
                ('area_add', models.TextField(blank=True, help_text='Scipt used to add an area to container', null=True, verbose_name='area_add')),
                ('user_add', models.TextField(blank=True, help_text='Script used to add a user to container', null=True, verbose_name='user_add')),
                ('user_del', models.TextField(blank=True, help_text='Script used to delete a user from container', null=True, verbose_name='user_del')),
                ('scope_add', models.TextField(blank=True, help_text='Script used to add a scope to container', null=True, verbose_name='scope_add')),
                ('scope_del', models.TextField(blank=True, help_text='Script used to delete a scope from container', null=True, verbose_name='scope_del')),
                ('user_to_scope', models.TextField(blank=True, help_text='Script used to link a user to a container', null=True, verbose_name='user_to_scope')),
                ('user_from_scope', models.TextField(blank=True, help_text='Script used to unlink a user from a container', null=True, verbose_name='user_from_scope')),
            ],
            options={
                'verbose_name': 'ContainerType',
                'verbose_name_plural': 'ContainerTypes',
            },
        ),
        migrations.CreateModel(
            name='Group',
            fields=[
                ('group_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='auth.group')),
            ],
            options={
                'verbose_name': 'Group',
                'verbose_name_plural': 'Groups',
            },
            bases=('auth.group',),
            managers=[
                ('objects', django.contrib.auth.models.GroupManager()),
            ],
        ),
        migrations.CreateModel(
            name='Client',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('desc', models.CharField(blank=True, max_length=80, null=True, verbose_name='desc')),
                ('text', models.TextField(blank=True, null=True, verbose_name='text')),
                ('ctime', models.DateTimeField(blank=True, null=True, verbose_name='ctime')),
                ('cuser', models.CharField(blank=True, max_length=8, null=True, verbose_name='cuser')),
                ('utime', models.DateTimeField(blank=True, null=True, verbose_name='utime')),
                ('uuser', models.CharField(blank=True, max_length=8, null=True, verbose_name='uuser')),
                ('key', models.CharField(max_length=20, unique=True, verbose_name='key')),
                ('organization', models.ForeignKey(blank=True, help_text='To support hirarchical structures like IGS and SVAs', null=True, on_delete=django.db.models.deletion.PROTECT, to='organization.client')),
            ],
            options={
                'verbose_name': 'Client',
                'verbose_name_plural': 'Clients',
            },
        ),
        migrations.CreateModel(
            name='Application',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
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
                ('client', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='organization.client')),
            ],
            options={
                'verbose_name': 'Application',
                'verbose_name_plural': 'Applications',
            },
        ),
        migrations.CreateModel(
            name='Container',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('desc', models.CharField(blank=True, max_length=80, null=True, verbose_name='desc')),
                ('text', models.TextField(blank=True, null=True, verbose_name='text')),
                ('ctime', models.DateTimeField(blank=True, null=True, verbose_name='ctime')),
                ('cuser', models.CharField(blank=True, max_length=8, null=True, verbose_name='cuser')),
                ('utime', models.DateTimeField(blank=True, null=True, verbose_name='utime')),
                ('uuser', models.CharField(blank=True, max_length=8, null=True, verbose_name='uuser')),
                ('key', models.CharField(max_length=20, unique=True, verbose_name='key')),
                ('connection', models.TextField(blank=True, help_text='Script to establish connection to container', max_length=200, null=True, verbose_name='Connection')),
                ('client', models.ForeignKey(blank=True, help_text='Defines ownership of container', null=True, on_delete=django.db.models.deletion.PROTECT, to='organization.client')),
                ('containertype', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='organization.containertype')),
            ],
            options={
                'verbose_name': 'Container',
                'verbose_name_plural': 'Containers',
            },
        ),
        migrations.CreateModel(
            name='Scope',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('desc', models.CharField(blank=True, max_length=80, null=True, verbose_name='desc')),
                ('text', models.TextField(blank=True, null=True, verbose_name='text')),
                ('ctime', models.DateTimeField(blank=True, null=True, verbose_name='ctime')),
                ('cuser', models.CharField(blank=True, max_length=8, null=True, verbose_name='cuser')),
                ('utime', models.DateTimeField(blank=True, null=True, verbose_name='utime')),
                ('uuser', models.CharField(blank=True, max_length=8, null=True, verbose_name='uuser')),
                ('key', models.CharField(default='tbd', max_length=80, unique=True, verbose_name='key')),
                ('business_unit_1', models.CharField(blank=True, max_length=80, null=True, verbose_name='business_unit_1')),
                ('business_unit_2', models.CharField(blank=True, max_length=80, null=True, verbose_name='business_unit_2')),
                ('business_unit_3', models.CharField(blank=True, max_length=80, null=True, verbose_name='business_unit_3')),
                ('business_unit_4', models.CharField(blank=True, max_length=80, null=True, verbose_name='business_unit_4')),
                ('business_unit_5', models.CharField(blank=True, max_length=80, null=True, verbose_name='business_unit_5')),
                ('team', models.CharField(blank=True, max_length=80, null=True, verbose_name='team')),
                ('app_scope', models.ForeignKey(blank=True, help_text='Here are the standard templates created by Abraxas or other provider', null=True, on_delete=django.db.models.deletion.PROTECT, related_name='+', to='organization.scope')),
                ('application', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='organization.application')),
                ('org_scope', models.ForeignKey(blank=True, help_text='Here are the standard templates created by the client', null=True, on_delete=django.db.models.deletion.PROTECT, related_name='+', to='organization.scope')),
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
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
                ('client', models.ForeignKey(blank=True, help_text='If specified, the user may only maintain client-related objects', null=True, on_delete=django.db.models.deletion.PROTECT, to='organization.client')),
                ('scopes', models.ManyToManyField(blank=True, to='organization.scope')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Area',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('desc', models.CharField(blank=True, max_length=80, null=True, verbose_name='desc')),
                ('text', models.TextField(blank=True, null=True, verbose_name='text')),
                ('ctime', models.DateTimeField(blank=True, null=True, verbose_name='ctime')),
                ('cuser', models.CharField(blank=True, max_length=8, null=True, verbose_name='cuser')),
                ('utime', models.DateTimeField(blank=True, null=True, verbose_name='utime')),
                ('uuser', models.CharField(blank=True, max_length=8, null=True, verbose_name='uuser')),
                ('key', models.CharField(max_length=20, verbose_name='key')),
                ('application', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='organization.application')),
                ('database', models.ForeignKey(help_text='To store structured data', on_delete=django.db.models.deletion.PROTECT, related_name='+', to='organization.container')),
                ('filestorage', models.ForeignKey(help_text='To store files', on_delete=django.db.models.deletion.PROTECT, related_name='+', to='organization.container')),
            ],
            options={
                'verbose_name': 'Area',
                'verbose_name_plural': 'Areas',
                'unique_together': {('application', 'key')},
            },
        ),
    ]
