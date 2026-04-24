from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_horimetroregistro'),
    ]

    operations = [
        migrations.AddField(
            model_name='horimetroregistro',
            name='horimetro',
            field=models.DecimalField(blank=True, decimal_places=1, max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name='horimetroregistro',
            name='maquinario',
            field=models.CharField(blank=True, default='', max_length=150),
        ),
        migrations.AddField(
            model_name='horimetroregistro',
            name='tipo_registro',
            field=models.CharField(choices=[('veiculo', 'Veiculo'), ('maquina', 'Maquina')], default='veiculo', max_length=10),
        ),
        migrations.AlterField(
            model_name='horimetroregistro',
            name='placa',
            field=models.CharField(blank=True, default='', max_length=8),
        ),
        migrations.AlterField(
            model_name='horimetroregistro',
            name='quilometragem',
            field=models.DecimalField(blank=True, decimal_places=1, max_digits=10, null=True),
        ),
        migrations.AlterField(
            model_name='horimetroregistro',
            name='veiculo',
            field=models.CharField(blank=True, default='', max_length=150),
        ),
    ]
