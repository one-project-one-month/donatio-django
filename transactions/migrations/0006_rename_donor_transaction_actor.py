# Generated by Django 5.2.3 on 2025-07-14 19:18

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("transactions", "0005_alter_transaction_title"),
    ]

    operations = [
        migrations.RenameField(
            model_name="transaction",
            old_name="donor",
            new_name="actor",
        ),
    ]
