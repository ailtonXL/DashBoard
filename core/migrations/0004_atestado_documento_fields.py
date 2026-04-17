from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_usuariocomrole'),
    ]

    operations = [
        migrations.AddField(
            model_name='atestado',
            name='classificacao',
            field=models.CharField(default='', max_length=120),
        ),
        migrations.AddField(
            model_name='atestado',
            name='crm_cro_cress',
            field=models.CharField(default='', max_length=40),
        ),
        migrations.AddField(
            model_name='atestado',
            name='empresa',
            field=models.CharField(default='', max_length=120),
        ),
        migrations.AddField(
            model_name='atestado',
            name='hora_retorno',
            field=models.TimeField(default='00:00'),
        ),
        migrations.AddField(
            model_name='atestado',
            name='hora_saida',
            field=models.TimeField(default='00:00'),
        ),
        migrations.AddField(
            model_name='atestado',
            name='medico',
            field=models.CharField(default='', max_length=120),
        ),
        migrations.AddField(
            model_name='atestado',
            name='tipo',
            field=models.CharField(
                choices=[
                    ('atestado_medico', 'Atestado Médico'),
                    ('declaracao_comparecimento', 'Declaração de Comparecimento'),
                    ('declaracao_obito', 'Declaração de óbito'),
                    ('certidao_nascimento', 'Certidão de Nascimento'),
                ],
                default='atestado_medico',
                max_length=40,
            ),
        ),
    ]
