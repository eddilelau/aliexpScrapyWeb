# Generated by Django 2.1.5 on 2019-07-12 14:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0006_remove_infringeproductinfo_test'),
    ]

    operations = [
        migrations.AddField(
            model_name='competingproductdailysales',
            name='allCategories',
            field=models.CharField(default='', max_length=128),
        ),
        migrations.AddField(
            model_name='competingproductdailysales',
            name='eigthCategory',
            field=models.CharField(default='', max_length=128),
        ),
        migrations.AddField(
            model_name='competingproductdailysales',
            name='fifthCategory',
            field=models.CharField(default='', max_length=128),
        ),
        migrations.AddField(
            model_name='competingproductdailysales',
            name='firstCategory',
            field=models.CharField(default='', max_length=128),
        ),
        migrations.AddField(
            model_name='competingproductdailysales',
            name='fourthCategory',
            field=models.CharField(default='', max_length=128),
        ),
        migrations.AddField(
            model_name='competingproductdailysales',
            name='home',
            field=models.CharField(default='', max_length=128),
        ),
        migrations.AddField(
            model_name='competingproductdailysales',
            name='secondCategory',
            field=models.CharField(default='', max_length=128),
        ),
        migrations.AddField(
            model_name='competingproductdailysales',
            name='seventhCategory',
            field=models.CharField(default='', max_length=128),
        ),
        migrations.AddField(
            model_name='competingproductdailysales',
            name='sixthCategory',
            field=models.CharField(default='', max_length=128),
        ),
        migrations.AddField(
            model_name='competingproductdailysales',
            name='thirdCategory',
            field=models.CharField(default='', max_length=128),
        ),
    ]
