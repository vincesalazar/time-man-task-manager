# Generated by Django 3.0.3 on 2020-04-19 10:09

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('time_man_app', '0002_collection_user'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='task',
            name='due_date',
        ),
    ]
