# Generated by Django 4.2.4 on 2023-11-06 12:41

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='vote',
            name='student',
        ),
        migrations.CreateModel(
            name='Voters',
            fields=[
                ('voterId', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('email', models.CharField(max_length=255)),
                ('pin', models.CharField(max_length=255)),
                ('student', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='home.student')),
            ],
        ),
        migrations.AddField(
            model_name='vote',
            name='voter',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='home.voters'),
        ),
    ]
