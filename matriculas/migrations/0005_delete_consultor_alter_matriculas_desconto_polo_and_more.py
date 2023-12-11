# Generated by Django 4.2.7 on 2023-12-09 19:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('matriculas', '0004_userprofile_cargo'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Consultor',
        ),
        migrations.AlterField(
            model_name='matriculas',
            name='desconto_polo',
            field=models.DecimalField(decimal_places=2, max_digits=6),
        ),
        migrations.AlterField(
            model_name='matriculas',
            name='desconto_total',
            field=models.DecimalField(decimal_places=2, max_digits=6),
        ),
    ]