# Generated by Django 5.0.3 on 2024-11-29 10:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('organization', '0003_remove_user_use_scope'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='application',
            name='business_unit_1',
        ),
        migrations.RemoveField(
            model_name='application',
            name='business_unit_2',
        ),
        migrations.RemoveField(
            model_name='application',
            name='business_unit_3',
        ),
        migrations.RemoveField(
            model_name='application',
            name='business_unit_4',
        ),
        migrations.RemoveField(
            model_name='application',
            name='business_unit_5',
        ),
        migrations.AddField(
            model_name='application',
            name='bu1_type',
            field=models.CharField(blank=True, max_length=80, null=True, verbose_name='Business_Unit_Type_1'),
        ),
        migrations.AddField(
            model_name='application',
            name='bu2_type',
            field=models.CharField(blank=True, max_length=80, null=True, verbose_name='Business_Unit_Type_2'),
        ),
        migrations.AddField(
            model_name='application',
            name='bu3_type',
            field=models.CharField(blank=True, max_length=80, null=True, verbose_name='Business_Unit_Type_3'),
        ),
        migrations.AddField(
            model_name='application',
            name='bu4_type',
            field=models.CharField(blank=True, max_length=80, null=True, verbose_name='Business_Unit_Type_4'),
        ),
        migrations.AddField(
            model_name='application',
            name='bu5_type',
            field=models.CharField(blank=True, max_length=80, null=True, verbose_name='Business_Unit_Type_5'),
        ),
    ]