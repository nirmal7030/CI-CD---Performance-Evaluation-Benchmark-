from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("bench", "0004_alter_metric_options_and_more"),
    ]

    # No schema changes here. We keep using the original long field names
    # on the Metric model (layer_cache_efficiency, pipeline_recovery_time, etc.)
    operations = []
