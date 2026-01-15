from django.db import migrations, models
import django.db.models.deletion


def forwards_func(apps, schema_editor):
    # Nothing special needed; field is nullable.
    pass


def reverse_func(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='courseenrollment',
            name='last_lesson',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='enrollment_last_seen', to='courses.lesson'),
        ),
    ]
