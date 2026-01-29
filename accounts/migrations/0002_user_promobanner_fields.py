from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='show_promo_banner',
            field=models.BooleanField(default=False, help_text='Show promo banner at top of site (owner only)'),
        ),
        migrations.AddField(
            model_name='user',
            name='promo_banner_text',
            field=models.CharField(max_length=255, blank=True, default='', help_text='Custom promo banner text'),
        ),
    ]
