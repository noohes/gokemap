# Generated by Django 2.2 on 2019-02-05 06:06

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='gym',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='미정', max_length=20)),
                ('is_pkstp', models.BooleanField(default=True)),
                ('x_cdn', models.CharField(default=-1, max_length=20)),
                ('y_cdn', models.CharField(default=-1, max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='pokemon',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='미정', max_length=20)),
                ('type_1', models.CharField(default='미정', max_length=4)),
                ('type_2', models.CharField(default='미정', max_length=4)),
                ('atk', models.IntegerField(default=-1)),
                ('df', models.IntegerField(default=-1)),
                ('stm', models.IntegerField(default=-1)),
                ('c_rate', models.IntegerField(default=-1)),
                ('r_rate', models.IntegerField(default=-1)),
            ],
        ),
        migrations.CreateModel(
            name='raid',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Tier', models.CharField(default=-1, max_length=5)),
                ('poke', models.ForeignKey(db_constraint=False, default=-1, on_delete=django.db.models.deletion.DO_NOTHING, related_name='raid', to='map.pokemon')),
            ],
        ),
        migrations.CreateModel(
            name='research',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('to_do', models.CharField(default='미정', max_length=50)),
                ('rwd', models.CharField(default='미정', max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='raid_ing',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('gym', models.OneToOneField(on_delete=django.db.models.deletion.DO_NOTHING, parent_link=True, to='map.gym')),
                ('s_time', models.DateTimeField()),
                ('poke', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='map.raid')),
            ],
        ),
    ]
