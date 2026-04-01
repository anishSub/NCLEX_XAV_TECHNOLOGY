from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('subscriptions', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subscription',
            name='duration',
            field=models.CharField(blank=True, choices=[('MONTHLY', '1 Month'), ('QUARTERLY', '3 Months'), ('YEARLY', '1 Year'), ('LIFETIME', 'Lifetime')], max_length=20, null=True),
        ),
    ]
