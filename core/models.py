from django.db import models
from django.contrib.auth.models import User


class Atestado(models.Model):
    TIPOS_DOCUMENTO = [
        ('atestado_medico', 'Atestado Médico'),
        ('declaracao_comparecimento', 'Declaração de Comparecimento'),
        ('declaracao_obito', 'Declaração de óbito'),
        ('certidao_nascimento', 'Certidão de Nascimento'),
    ]

    UF_CHOICES = [
        ('AC', 'AC - Acre'), ('AL', 'AL - Alagoas'), ('AP', 'AP - Amapá'),
        ('AM', 'AM - Amazonas'), ('BA', 'BA - Bahia'), ('CE', 'CE - Ceará'),
        ('DF', 'DF - Distrito Federal'), ('ES', 'ES - Espírito Santo'),
        ('GO', 'GO - Goiás'), ('MA', 'MA - Maranhão'), ('MT', 'MT - Mato Grosso'),
        ('MS', 'MS - Mato Grosso do Sul'), ('MG', 'MG - Minas Gerais'),
        ('PA', 'PA - Pará'), ('PB', 'PB - Paraíba'), ('PR', 'PR - Paraná'),
        ('PE', 'PE - Pernambuco'), ('PI', 'PI - Piauí'), ('RJ', 'RJ - Rio de Janeiro'),
        ('RN', 'RN - Rio Grande do Norte'), ('RS', 'RS - Rio Grande do Sul'),
        ('RO', 'RO - Rondônia'), ('RR', 'RR - Roraima'),
        ('SC', 'SC - Santa Catarina'), ('SP', 'SP - São Paulo'),
        ('SE', 'SE - Sergipe'), ('TO', 'TO - Tocantins'),
    ]

    nome = models.CharField(max_length=120)
    empresa = models.CharField(max_length=120, default='')
    tipo = models.CharField(max_length=40, choices=TIPOS_DOCUMENTO, default='atestado_medico')
    data_inicio = models.DateField()
    hora_saida = models.TimeField(default='00:00')
    data_fim = models.DateField()
    hora_retorno = models.TimeField(default='00:00')
    classificacao = models.CharField(max_length=20, default='', blank=True)
    uf = models.CharField(max_length=2, choices=UF_CHOICES, default='SP')
    medico = models.CharField(max_length=120, default='')
    crm_cro_cress = models.CharField(max_length=40, default='')

    arquivo = models.FileField(upload_to='atestados/')
    processado = models.BooleanField(default=False)

    dias_afastado = models.PositiveIntegerField(default=0)
    absenteismo = models.FloatField(default=0)  # 👈 novo campo

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nome

    def calcular_metricas(self):
        """Atualiza dias_afastado e absenteismo automaticamente."""
        # Calcular dias de afastamento
        self.dias_afastado = max((self.data_fim - self.data_inicio).days + 1, 0)
        
        # Calcular absenteísmo (% de 22 dias úteis por mês)
        dias_uteis = 22
        if dias_uteis > 0:
            self.absenteismo = round((self.dias_afastado / dias_uteis) * 100, 2)
        else:
            self.absenteismo = 0
        
        # Marcar como processado
        self.processado = True

    def save(self, *args, **kwargs):
        """Override save para calcular métricas antes de salvar."""
        self.calcular_metricas()
        super().save(*args, **kwargs)


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
