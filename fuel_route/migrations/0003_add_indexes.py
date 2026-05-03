from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('fuel_route', '0002_alter_fuelstation_opis_id'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='fuelstation',
            index=models.Index(fields=['latitude', 'longitude'], name='location_idx'),
        ),
        migrations.AddIndex(
            model_name='fuelstation',
            index=models.Index(fields=['retail_price'], name='price_idx'),
        ),
    ]
