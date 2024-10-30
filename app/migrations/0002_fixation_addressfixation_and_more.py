# Generated by Django 4.2.4 on 2024-10-20 10:01

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('app', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Fixation',
            fields=[
                ('fixation_id', models.AutoField(primary_key=True, serialize=False)),
                ('month', models.IntegerField(default=0, verbose_name='Месяц')),
                ('created_at', models.DateTimeField(blank=True, null=True)),
                ('submitted_at', models.DateTimeField(blank=True, null=True)),
                ('completed_at', models.DateTimeField(blank=True, null=True)),
                ('status', models.IntegerField(blank=True, choices=[(1, 'Введён'), (2, 'В работе'), (3, 'Завершен'), (4, 'Отклонен'), (5, 'Удален')], default=1, null=True)),
                ('moderator', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='moderator', to=settings.AUTH_USER_MODEL, verbose_name='Модератор')),
                ('owner', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='owner', to=settings.AUTH_USER_MODEL, verbose_name='Пользователь')),
            ],
            options={
                'verbose_name': 'Фиксация',
                'verbose_name_plural': 'Фиксации',
                'db_table': 'fixations',
                'ordering': ('-submitted_at',),
            },
        ),
        migrations.CreateModel(
            name='AddressFixation',
            fields=[
                ('mm_id', models.AutoField(primary_key=True, serialize=False)),
                ('value', models.IntegerField(blank=True, null=True, verbose_name='Поле м-м')),
                ('address', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='app.address')),
                ('fixation', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='app.fixation')),
            ],
            options={
                'verbose_name': 'м-м',
                'verbose_name_plural': 'м-м',
                'db_table': 'address_fixation',
                'managed': True,
            },
        ),
        migrations.AddConstraint(
            model_name='addressfixation',
            constraint=models.UniqueConstraint(fields=('address', 'fixation'), name='unique_AddressFixation'),
        ),
    ]