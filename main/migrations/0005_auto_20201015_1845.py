# Generated by Django 3.0.3 on 2020-10-15 23:45

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0004_auto_20201015_1839'),
    ]

    operations = [
        migrations.AlterField(
            model_name='noticia',
            name='fuente',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='main.Fuente'),
        ),
    ]