from django.contrib import admin
from .models import Atestado, HorimetroRegistro, UsuarioComRole

@admin.register(Atestado)
class AtestadoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'data_inicio', 'data_fim', 'dias_afastado', 'absenteismo', 'processado')
    search_fields = ('nome',)
    list_filter = ('processado', 'created_at')

@admin.register(UsuarioComRole)
class UsuarioComRoleAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'is_gerencia', 'created_at')
    search_fields = ('user__username',)
    list_filter = ('role', 'is_gerencia')


@admin.register(HorimetroRegistro)
class HorimetroRegistroAdmin(admin.ModelAdmin):
    list_display = ('tipo_registro', 'veiculo', 'maquinario', 'placa', 'data_registro', 'quilometragem', 'horimetro', 'created_at')
    search_fields = ('veiculo', 'maquinario', 'placa')
    list_filter = ('tipo_registro', 'data_registro')
