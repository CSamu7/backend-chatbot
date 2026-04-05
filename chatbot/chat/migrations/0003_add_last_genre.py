from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0002_alter_chat_options_alter_message_options'),
    ]

    operations = [
        migrations.AddField(
            model_name='chat',
            name='last_genre',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
