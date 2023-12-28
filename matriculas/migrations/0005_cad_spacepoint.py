# Generated by Django 4.2.7 on 2023-12-26 19:31

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('matriculas', '0004_alter_cad_cursos_tipo_curso_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='cad_spacepoint',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('data_spacepoint', models.DateTimeField()),
                ('ativo', models.BooleanField(default=True)),
                ('id_processos', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='matriculas.cad_processo')),
            ],
            options={
                'db_table': 'spacepoint',
            },
        ),
    ]
