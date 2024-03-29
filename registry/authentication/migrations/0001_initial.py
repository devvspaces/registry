# Generated by Django 4.0 on 2023-02-03 19:16

from django.db import migrations, models
import django.db.models.deletion
import utils.base.validators


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Partner',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('partner', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='other_partner', to='authentication.partner')),
            ],
        ),
        migrations.CreateModel(
            name='PendingRelationship',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, validators=[utils.base.validators.validate_special_char])),
                ('country', models.CharField(blank=True, max_length=60)),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('email', models.EmailField(max_length=255, unique=True)),
                ('verified_email', models.BooleanField(default=False)),
                ('active', models.BooleanField(default=False)),
                ('staff', models.BooleanField(default=False)),
                ('admin', models.BooleanField(default=False)),
                ('start_date', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'User',
            },
        ),
        migrations.CreateModel(
            name='Relationship',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('dating', 'Dating'), ('married', 'Married')], default='dating', max_length=10)),
                ('verified', models.BooleanField(default=False)),
                ('partners', models.ManyToManyField(to='authentication.Partner')),
            ],
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fullname', models.CharField(max_length=50, validators=[utils.base.validators.validate_special_char])),
                ('sex', models.CharField(blank=True, choices=[('M', 'Male'), ('F', 'Female')], max_length=1)),
                ('country', models.CharField(blank=True, max_length=60)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='authentication.user')),
            ],
        ),
        migrations.CreateModel(
            name='Phone',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('phoneno', models.CharField(help_text='Enter a correct phone number', max_length=16, validators=[utils.base.validators.validate_phone])),
                ('verified', models.BooleanField(default=False)),
                ('profile', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='authentication.profile')),
            ],
        ),
        migrations.CreateModel(
            name='PendingRelationshipPhone',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('phoneno', models.CharField(help_text='Enter a correct phone number', max_length=16, validators=[utils.base.validators.validate_phone])),
                ('verified', models.BooleanField(default=False)),
                ('pending_relationship', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='authentication.pendingrelationship')),
            ],
        ),
        migrations.AddField(
            model_name='pendingrelationship',
            name='creator',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='creator', to='authentication.profile'),
        ),
        migrations.AddField(
            model_name='partner',
            name='pending_relationship',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='authentication.pendingrelationship'),
        ),
        migrations.AddField(
            model_name='partner',
            name='profile',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to='authentication.profile'),
        ),
    ]
