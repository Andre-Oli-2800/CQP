# Generated by Django 3.0.10 on 2024-03-23 22:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fornecedor',
            name='cnpj',
            field=models.BigIntegerField(primary_key=True, serialize=False),
        ),
    ]
