# Generated by Django 4.2.4 on 2023-08-18 10:33

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0008_customer_password_alter_customer_user'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customer',
            name='password',
        ),
    ]