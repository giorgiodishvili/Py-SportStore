# SportStore/migrations/0001_initial.py

from django.db import migrations, models


def create_initial_products(apps, schema_editor):
    Product = apps.get_model('SportStore', 'Product')
    Product.objects.create(
        name="Basketball",
        description="A high-quality basketball for indoor and outdoor play.",
        price=29.99,
        image_url="https://example.com/images/basketball.jpg"
    )
    Product.objects.create(
        name="Tennis Racket",
        description="Lightweight and durable tennis racket.",
        price=49.99,
        image_url="https://example.com/images/tennis_racket.jpg"
    )
    Product.objects.create(
        name="Football",
        description="Professional-grade football for all levels of play.",
        price=39.99,
        image_url="https://example.com/images/football.jpg"
    )


class Migration(migrations.Migration):
    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField()),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('image_url', models.URLField(blank=True, max_length=200)),
            ],
        ),
        migrations.RunPython(create_initial_products),
    ]
