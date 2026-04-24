from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_alter_atestado_classificacao_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='HorimetroRegistro',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('veiculo', models.CharField(max_length=150)),
                ('placa', models.CharField(max_length=8)),
                ('data_registro', models.DateField()),
                ('quilometragem', models.DecimalField(decimal_places=1, max_digits=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'Registro de Horimetro',
                'verbose_name_plural': 'Registros de Horimetro',
                'ordering': ['-data_registro', '-created_at'],
            },
        ),
    ]