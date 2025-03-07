# Generated by Django 5.1.6 on 2025-03-02 12:18

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('vendedores', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Venda',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('valor_total', models.DecimalField(decimal_places=2, max_digits=10)),
                ('valor_comissao', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('data_venda', models.DateTimeField(default=django.utils.timezone.now)),
                ('vendedor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='vendas', to='vendedores.vendedor')),
            ],
            options={
                'verbose_name': 'Venda',
                'verbose_name_plural': 'Vendas',
                'ordering': ['-data_venda'],
            },
        ),
    ]
