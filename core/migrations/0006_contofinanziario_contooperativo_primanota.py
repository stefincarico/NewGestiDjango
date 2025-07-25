# Generated by Django 5.2.4 on 2025-07-23 15:56

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_scadenza'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ContoFinanziario',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('attivo', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('nome_conto', models.CharField(max_length=100, unique=True)),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Conto Finanziario',
                'verbose_name_plural': 'Conti Finanziari',
            },
        ),
        migrations.CreateModel(
            name='ContoOperativo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('attivo', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('nome_conto', models.CharField(max_length=100, unique=True)),
                ('tipo', models.CharField(choices=[('Costo', 'Costo'), ('Ricavo', 'Ricavo')], max_length=20)),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Conto Operativo',
                'verbose_name_plural': 'Conti Operativi',
            },
        ),
        migrations.CreateModel(
            name='PrimaNota',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('attivo', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('data', models.DateField(help_text='Data di registrazione del movimento')),
                ('descrizione', models.CharField(max_length=255)),
                ('importo', models.DecimalField(decimal_places=2, max_digits=10)),
                ('tipo_movimento', models.CharField(choices=[('Entrata', 'Entrata'), ('Uscita', 'Uscita'), ('Giroconto', 'Giroconto')], max_length=20)),
                ('anagrafica', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='core.anagrafica')),
                ('cantiere', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='core.cantiere')),
                ('conto_finanziario', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='movimenti', to='core.contofinanziario')),
                ('conto_operativo', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='core.contooperativo')),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('movimento_collegato', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='giroconto_associato', to='core.primanota')),
                ('scadenza_collegata', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='pagamenti', to='core.scadenza')),
                ('updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Movimento di Prima Nota',
                'verbose_name_plural': 'Prima Nota',
                'ordering': ['-data'],
            },
        ),
    ]
