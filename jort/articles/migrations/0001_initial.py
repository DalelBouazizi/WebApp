# Generated by Django 5.0.6 on 2024-07-02 08:16

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Article',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('titre', models.CharField(max_length=200)),
                ('date', models.CharField(max_length=100)),
                ('contenu', models.TextField()),
            ],
        ),
    ]
