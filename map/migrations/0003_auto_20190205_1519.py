# Generated by Django 2.2 on 2019-02-05 06:19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('map', '0002_auto_20190205_1509'),
    ]

    operations = [
        migrations.AlterField(
            model_name='raid_ing',
            name='gym',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='map.gym'),
        ),
    ]
