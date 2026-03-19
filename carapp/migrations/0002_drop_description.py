from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("carapp", "0001_initial"),
    ]

    operations = [
        migrations.RunSQL(
            sql="""ALTER TABLE carapp_contact DROP COLUMN IF EXISTS description;""",
            reverse_sql="""ALTER TABLE carapp_contact ADD COLUMN description LONGTEXT NOT NULL DEFAULT '';""",
        ),
    ]
