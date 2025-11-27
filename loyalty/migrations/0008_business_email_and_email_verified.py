from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('loyalty', '0007_rename_stamp_count_wallet_points_balance_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='business',
            name='email',
            field=models.EmailField(blank=True, max_length=254),
        ),
        migrations.AddField(
            model_name='business',
            name='email_verified',
            field=models.BooleanField(default=False),
        ),
    ]


