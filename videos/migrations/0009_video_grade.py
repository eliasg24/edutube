# Generated by Django 4.1.13 on 2024-05-26 16:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('videos', '0008_alter_video_sector'),
    ]

    operations = [
        migrations.AddField(
            model_name='video',
            name='grade',
            field=models.TextField(blank=True, choices=[('1° grado', '1° grado'), ('2° grado', '2° grado'), ('3° grado', '3° grado'), ('4° grado', '4° grado'), ('5° grado', '5° grado'), ('6° grado', '6° grado'), ('7° grado', '7° grado'), ('8° grado', '8° grado'), ('9° grado', '9° grado'), ('1° grado (prepa)', '1° grado (prepa)'), ('2° grado (prepa)', '2° grado (prepa)')], null=True),
        ),
    ]
