from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('loyalty', '0006_business_slug'),
        ('reviews', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Service',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=150)),
                ('category', models.CharField(choices=[('food', 'غذا'), ('cafe', 'کافه'), ('beauty', 'خدمات زیبایی'), ('fitness', 'ورزشی'), ('other', 'سایر')], default='other', max_length=32)),
                ('description', models.TextField(blank=True)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('business', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='services', to='loyalty.business')),
            ],
            options={
                'ordering': ('name',),
                'unique_together': {('business', 'name')},
            },
        ),
        migrations.AddField(
            model_name='review',
            name='admin_note',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='review',
            name='moderated_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='moderated_reviews', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='review',
            name='service',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='reviews', to='reviews.service'),
        ),
        migrations.AddField(
            model_name='review',
            name='source',
            field=models.CharField(choices=[('app', 'Mobile App'), ('web', 'Website'), ('admin', 'Admin Panel')], default='app', max_length=12),
        ),
        migrations.AddField(
            model_name='review',
            name='status',
            field=models.CharField(choices=[('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')], default='approved', max_length=12),
        ),
        migrations.AddField(
            model_name='review',
            name='target_type',
            field=models.CharField(choices=[('business', 'Business'), ('service', 'Service')], default='business', max_length=12),
        ),
        migrations.AddField(
            model_name='review',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='review',
            name='rating',
            field=models.PositiveSmallIntegerField(),
        ),
        migrations.AlterUniqueTogether(
            name='review',
            unique_together=set(),
        ),
        migrations.AddIndex(
            model_name='review',
            index=models.Index(fields=('status',), name='reviews_re_status_aaaa3f_idx'),
        ),
        migrations.AddIndex(
            model_name='review',
            index=models.Index(fields=('target_type',), name='reviews_re_target__5542d3_idx'),
        ),
        migrations.CreateModel(
            name='ReviewResponse',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.TextField()),
                ('is_public', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('responder', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='review_responses', to=settings.AUTH_USER_MODEL)),
                ('review', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='responses', to='reviews.review')),
            ],
            options={
                'ordering': ('-created_at',),
            },
        ),
    ]

