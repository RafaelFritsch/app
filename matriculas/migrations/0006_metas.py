# Generated by Django 4.2.7 on 2023-12-27 11:23

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('matriculas', '0005_cad_spacepoint'),
    ]

    operations = [
        migrations.CreateModel(
            name='Metas',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('meta', models.IntegerField()),
                ('polo', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='matriculas.cad_polos')),
                ('processo', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='matriculas.cad_processo')),
                ('tipo_curso', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='matriculas.tipo_curso')),
            ],
            options={
                'db_table': 'metas',
            },
        ),
    ]