# Generated by Django 4.2.7 on 2023-12-27 20:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('matriculas', '0006_metas'),
    ]

    operations = [
        migrations.AddField(
            model_name='cad_spacepoint',
            name='meta_pc',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
    ]