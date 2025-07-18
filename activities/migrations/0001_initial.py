# Generated by Django 5.2.3 on 2025-07-11 07:06

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("organizations", "0002_organization_kpay_qr_url_organization_type_and_more"),
        ("transactions", "0002_alter_transaction_amount"),
    ]

    operations = [
        migrations.CreateModel(
            name="Activity",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("title", models.CharField(max_length=255)),
                ("description", models.TextField(blank=True, null=True)),
                ("location", models.CharField(blank=True, max_length=255, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "organization",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="activities",
                        to="organizations.organization",
                    ),
                ),
            ],
            options={
                "verbose_name": "Activity",
                "verbose_name_plural": "Activities",
                "ordering": ["-created_at"],
            },
        ),
        migrations.CreateModel(
            name="ActivityTransaction",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("linked_at", models.DateTimeField(auto_now_add=True)),
                (
                    "activity",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="transaction_links",
                        to="activities.activity",
                    ),
                ),
                (
                    "transaction",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="activity_links",
                        to="transactions.transaction",
                    ),
                ),
            ],
            options={
                "verbose_name": "Activity Transaction Link",
                "verbose_name_plural": "Activity Transaction Links",
                "ordering": ["-linked_at"],
                "unique_together": {("activity", "transaction")},
            },
        ),
    ]
