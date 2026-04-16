from django.db import models


class Atestado(models.Model):
    nome = models.CharField(max_length=120)
    data_inicio = models.DateField()
    data_fim = models.DateField()

    arquivo = models.FileField(upload_to='atestados/')
    processado = models.BooleanField(default=False)

    dias_afastado = models.PositiveIntegerField(default=0)
    absenteismo = models.FloatField(default=0)  # 👈 novo campo

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nome