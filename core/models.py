from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
import base64
import hashlib

from cryptography.fernet import Fernet


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

    nome = models.CharField(max_length=512)
    empresa = models.CharField(max_length=512, default='')
    tipo = models.CharField(max_length=40, choices=TIPOS_DOCUMENTO, default='atestado_medico')
    data_inicio = models.DateField()
    hora_saida = models.TimeField(default='00:00')
    data_fim = models.DateField()
    hora_retorno = models.TimeField(default='00:00')
    classificacao = models.CharField(max_length=512, default='', blank=True)
    uf = models.CharField(max_length=2, choices=UF_CHOICES, default='SP')
    medico = models.CharField(max_length=512, default='')
    crm_cro_cress = models.CharField(max_length=512, default='')

    arquivo = models.FileField(upload_to='atestados/')
    processado = models.BooleanField(default=False)

    dias_afastado = models.PositiveIntegerField(default=0)
    absenteismo = models.FloatField(default=0)  # 👈 novo campo

    created_at = models.DateTimeField(auto_now_add=True)

    SENSITIVE_FIELDS = ['nome', 'empresa', 'classificacao', 'medico', 'crm_cro_cress']
    ENC_PREFIX = 'enc::'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._decrypt_sensitive_fields()

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
        self._encrypt_sensitive_fields()
        self.calcular_metricas()
        super().save(*args, **kwargs)
        self._decrypt_sensitive_fields()

    @classmethod
    def _get_fernet(cls):
        key_from_env = getattr(settings, 'FIELD_ENCRYPTION_KEY', '')
        if key_from_env:
            return Fernet(key_from_env.encode())

        # Fallback determinístico com SECRET_KEY para não quebrar ambiente local.
        derived_key = base64.urlsafe_b64encode(
            hashlib.sha256(settings.SECRET_KEY.encode()).digest()
        )
        return Fernet(derived_key)

    @classmethod
    def _encrypt_value(cls, value):
        if not value:
            return value
        if isinstance(value, str) and value.startswith(cls.ENC_PREFIX):
            return value
        token = cls._get_fernet().encrypt(str(value).encode()).decode()
        return f"{cls.ENC_PREFIX}{token}"

    @classmethod
    def _decrypt_value(cls, value):
        if not value or not isinstance(value, str):
            return value
        if not value.startswith(cls.ENC_PREFIX):
            return value
        token = value[len(cls.ENC_PREFIX):]
        try:
            return cls._get_fernet().decrypt(token.encode()).decode()
        except Exception:
            return value

    def _encrypt_sensitive_fields(self):
        for field_name in self.SENSITIVE_FIELDS:
            value = getattr(self, field_name, '')
            setattr(self, field_name, self._encrypt_value(value))

    def _decrypt_sensitive_fields(self):
        for field_name in self.SENSITIVE_FIELDS:
            value = getattr(self, field_name, '')
            setattr(self, field_name, self._decrypt_value(value))


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
    precisa_alterar_senha = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"


class HorimetroRegistro(models.Model):
    TIPO_REGISTRO_CHOICES = [
        ('veiculo', 'Veiculo'),
        ('maquina', 'Maquina'),
    ]

    tipo_registro = models.CharField(max_length=10, choices=TIPO_REGISTRO_CHOICES, default='veiculo')
    veiculo = models.CharField(max_length=150, blank=True, default='')
    maquinario = models.CharField(max_length=150, blank=True, default='')
    placa = models.CharField(max_length=8, blank=True, default='')
    data_registro = models.DateField()
    quilometragem = models.DecimalField(max_digits=10, decimal_places=1, null=True, blank=True)
    horimetro = models.DecimalField(max_digits=10, decimal_places=1, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-data_registro', '-created_at']
        verbose_name = 'Registro de Horimetro'
        verbose_name_plural = 'Registros de Horimetro'

    def save(self, *args, **kwargs):
        self.placa = (self.placa or '').upper().replace('-', '').replace(' ', '')
        if self.tipo_registro == 'maquina':
            self.veiculo = ''
            self.placa = ''
            self.quilometragem = None
        else:
            self.maquinario = ''
            self.horimetro = None
        super().save(*args, **kwargs)

    def __str__(self):
        nome = self.maquinario if self.tipo_registro == 'maquina' else self.veiculo
        return f"{self.get_tipo_registro_display()} - {nome}"
