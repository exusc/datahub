# Generated by Django 5.0.3 on 2024-06-21 19:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('organization', '0003_rename_client_owner_alter_owner_options_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='user',
            options={'verbose_name': 'User', 'verbose_name_plural': 'Users'},
        ),
        migrations.AddField(
            model_name='scope',
            name='type',
            field=models.CharField(choices=[('S', 'Standard'), ('O', 'Organization'), ('A', 'Application')], default='S', max_length=1, verbose_name='type'),
        ),
    ]