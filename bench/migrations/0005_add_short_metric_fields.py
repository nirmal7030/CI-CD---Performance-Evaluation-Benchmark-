from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("bench", "0004_alter_metric_options_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="metric",
            name="lce",
            field=models.FloatField(default=0.0),
        ),
        migrations.AddField(
            model_name="metric",
            name="prt",
            field=models.FloatField(default=0.0),
        ),
        migrations.AddField(
            model_name="metric",
            name="smo",
            field=models.FloatField(default=0.0),
        ),
        migrations.AddField(
            model_name="metric",
            name="dept",
            field=models.FloatField(default=0.0),
        ),
        migrations.AddField(
            model_name="metric",
            name="clbc",
            field=models.FloatField(default=0.0),
        ),
    ]
