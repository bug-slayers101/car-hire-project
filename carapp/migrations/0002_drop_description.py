from django.db import migrations


def drop_description(apps, schema_editor):
    # SQLite does not support DROP COLUMN directly; no-op when using sqlite.
    if schema_editor.connection.vendor == 'sqlite':
        return
    schema_editor.execute("ALTER TABLE carapp_contact DROP COLUMN IF EXISTS description;")


def add_description(apps, schema_editor):
    if schema_editor.connection.vendor == 'sqlite':
        return
    schema_editor.execute("ALTER TABLE carapp_contact ADD COLUMN description LONGTEXT NOT NULL DEFAULT '';")


class Migration(migrations.Migration):

    dependencies = [
        ("carapp", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(drop_description, reverse_code=add_description),
    ]
