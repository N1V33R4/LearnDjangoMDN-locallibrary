# Generated by Django 4.2.2 on 2023-07-05 15:07

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0003_alter_book_options_bookinstance_borrower'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='bookinstance',
            options={'ordering': ['due_back'], 'permissions': (('can mark returned', 'Set book as returned'),)},
        ),
    ]