# Generated by Django 5.2.1 on 2025-06-27 20:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('atelier', '0009_order_work_report'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='social_link',
            field=models.URLField(blank=True, verbose_name='Ссылка на соцсеть'),
        ),
    ]
