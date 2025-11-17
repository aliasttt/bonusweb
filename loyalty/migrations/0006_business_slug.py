from django.db import migrations, models
from django.utils.text import slugify


def populate_business_slugs(apps, schema_editor):
    Business = apps.get_model('loyalty', 'Business')
    for business in Business.objects.filter(slug__isnull=True):
        base_slug = slugify(business.name)[:200] or f"business-{business.pk}"
        slug = base_slug
        counter = 1
        while Business.objects.filter(slug=slug).exclude(pk=business.pk).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1
        business.slug = slug
        business.save(update_fields=['slug'])


class Migration(migrations.Migration):

    dependencies = [
        ('loyalty', '0005_add_is_reward_to_product'),
    ]

    operations = [
        migrations.AddField(
            model_name='business',
            name='slug',
            field=models.SlugField(blank=True, max_length=220, null=True, unique=True),
        ),
        migrations.RunPython(populate_business_slugs, migrations.RunPython.noop),
    ]

