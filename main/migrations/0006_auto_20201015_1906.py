# Generated by Django 3.0.3 on 2020-10-16 00:06

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0005_auto_20201015_1845'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fuente',
            name='categoria',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='main.Categoria'),
        ),
        migrations.AlterField(
            model_name='preferencia',
            name='noticia',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='main.Noticia'),
        ),
    ]
