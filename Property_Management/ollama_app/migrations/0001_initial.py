# Generated by Django 4.2.17 on 2024-12-30 09:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Hotel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('city', models.CharField(max_length=255)),
                ('hotel_id', models.CharField(max_length=255)),
                ('title', models.CharField(max_length=255)),
                ('location', models.CharField(max_length=255)),
                ('price', models.FloatField(blank=True, null=True)),
                ('image_path', models.CharField(max_length=255)),
                ('rating', models.FloatField(blank=True, null=True)),
                ('room_type', models.CharField(blank=True, max_length=255, null=True)),
                ('latitude', models.FloatField(blank=True, null=True)),
                ('longitude', models.FloatField(blank=True, null=True)),
            ],
            options={
                'db_table': 'hotels',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='PropertyContent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('hotel', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='content', to='ollama_app.hotel')),
            ],
            options={
                'db_table': 'property_content',
            },
        ),
        migrations.CreateModel(
            name='PropertySummary',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('summary', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('property', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='summaries', to='ollama_app.propertycontent')),
            ],
            options={
                'db_table': 'property_summaries',
            },
        ),
        migrations.CreateModel(
            name='PropertyReview',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rating', models.DecimalField(decimal_places=1, max_digits=3)),
                ('review', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('property', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reviews', to='ollama_app.propertycontent')),
            ],
            options={
                'db_table': 'property_reviews',
            },
        ),
    ]
