from django.db import models
from django.contrib.auth.models import User


class Atestado(models.Model):
    TIPOS_DOCUMENTO = [
        ('atestado_medico', 'Atestado Médico'),
        ('declaracao_comparecimento', 'Declaração de Comparecimento'),
        ('declaracao_obito', 'Declaração de óbito'),
        ('certidao_nascimento', 'Certidão de Nascimento'),
    ]

    nome = models.CharField(max_length=120)
    empresa = models.CharField(max_length=120, default='')
    tipo = models.CharField(max_length=40, choices=TIPOS_DOCUMENTO, default='atestado_medico')
    data_inicio = models.DateField()
    hora_saida = models.TimeField(default='00:00')
    data_fim = models.DateField()
    hora_retorno = models.TimeField(default='00:00')
    classificacao = models.CharField(max_length=120, default='')
    medico = models.CharField(max_length=120, default='')
    crm_cro_cress = models.CharField(max_length=40, default='')

    arquivo = models.FileField(upload_to='atestados/')
    processado = models.BooleanField(default=False)

    dias_afastado = models.PositiveIntegerField(default=0)
    absenteismo = models.FloatField(default=0)  # 👈 novo campo

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nome


class UsuarioComRole(models.Model):
    ROLES = [
        ('admin', 'Administração'),
        ('gerencia', 'Gerência'),
        ('logistica', 'Logística'),
        ('manutencao', 'Manutenção'),
        ('meio_ambiente', 'Meio Ambiente'),
        ('operacoes', 'Operações'),
        ('qualidade', 'Qualidade e Processos'),
        ('saude', 'Saúde e Segurança'),
        ('suprimentos', 'Suprimentos'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='role_profile')
    role = models.CharField(max_length=20, choices=ROLES)
    is_gerencia = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"
