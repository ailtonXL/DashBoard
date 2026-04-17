# 📊 Lógica de Contabilização de Documentos

## Resumo

A contabilização de documentos (atestados) foi implementada com **cálculo automático** de métri cas quando um documento é criado ou editado.

## Fluxo de Contabilização

### 1️⃣ Criação de Documento

```
Usuário submete formulário
        ↓
AtestadoForm valida dados
        ↓
Atestado.save() é chamado
        ↓
calcular_metricas() é executado automaticamente
        ↓
dias_afastado = diferença em dias (data_fim - data_inicio + 1)
absenteismo = (dias_afastado / 22 dias úteis) * 100
processado = True
        ↓
Documento salvo no banco com métricas calculadas
```

### 2️⃣ Métricas Calculadas

| Campo | Cálculo | Exemplo |
|-------|---------|---------|
| **dias_afastado** | `(data_fim - data_inicio).days + 1` | 5 dias |
| **absenteismo** | `(dias_afastado / 22) * 100` | 22.73% |
| **processado** | Sempre `True` após calcular | ✓ |

### 3️⃣ Agregação por Área

Cada departamento exibe 4 KPIs via `build_area_context()`:

```
Total de Documentos  →  COUNT(*) WHERE processado=True
  
Documentos no Mês  →  COUNT(*) WHERE processado=True AND created_at >= 1º do mês

Dias Afastados (Mês)  →  SUM(dias_afastado) WHERE processado=True AND created_at >= 1º do mês

Absenteismo Médio  →  AVG(absenteismo) WHERE processado=True AND absenteismo > 0
```

### 4️⃣ Dashboard Central

- **Gráfico Pizza**: Top 10 pessoas com maior absenteismo (processado=True)
- **Dados**: Títulos (nomes) + Valores (absenteismo %)

### 5️⃣ Administração

- **Tabela Ranking**: Top 10 documentos processados, ordenados por absenteismo DESC
- **Total Dias**: Soma de todos dias_afastado dos documentos processados

## ⚙️ Como Usar

### Criar Novo Documento (Automático)

```python
# Via formulário (POST)
# O save() é chamado automaticamente
# Métricas calculadas automaticamente
```

### Reprocessar Documentos Antigos

Se havia documentos criados **antes** da implementação:

```bash
# Reprocessar apenas documentos não processados
python manage.py reprocessar_documentos

# Reprocessar TODOS os documentos
python manage.py reprocessar_documentos --all
```

### Acesso Direto via Admin Django

```python
from core.models import Atestado

# Criar novo
doc = Atestado(
    nome="João Silva",
    data_inicio="2025-01-01",
    data_fim="2025-01-05"
)
doc.save()  # Métricas calculadas automaticamente

# Atualizar
doc.data_fim = "2025-01-10"
doc.save()  # Métricas recalculadas
```

## 🔍 Validação

Checklist de funcionalidade:

- ✅ Novo documento cadastrado → `dias_afastado` calculado
- ✅ Novo documento cadastrado → `absenteismo` calculado (% de 22 dias)
- ✅ Novo documento cadastrado → `processado = True`
- ✅ Dashboard mostra apenas documentos processados
- ✅ KPIs de área filtram por `processado=True`
- ✅ Gráfico mostra top 10 por absenteismo
- ✅ Absenteismo médio exclui valores 0

## 📝 Campos do Modelo

```python
class Atestado(models.Model):
    # Dados básicos
    nome: CharField
    empresa: CharField
    tipo: CharField (choices)
    
    # Período
    data_inicio: DateField
    data_fim: DateField
    hora_saida: TimeField
    hora_retorno: TimeField
    
    # Informações adicionais
    classificacao: CharField
    medico: CharField
    crm_cro_cress: CharField
    
    # Métricas (preenchidas automaticamente)
    dias_afastado: PositiveIntegerField  ← AUTOMÁTICO
    absenteismo: FloatField  ← AUTOMÁTICO
    processado: BooleanField  ← AUTOMÁTICO
    
    # Administrativo
    arquivo: FileField
    created_at: DateTimeField
```

## 🐛 Troubleshooting

**Q: Documentos antigos não mostram absenteismo?**
A: Execute `python manage.py reprocessar_documentos`

**Q: Absenteismo calculado errado?**
A: Verifique `data_inicio` e `data_fim`. Fórmula: `(dias_afastado / 22) * 100`

**Q: Gráfico vazio?**
A: Certifique-se de que documentos têm `processado=True` (rode reprocessar_documentos)

## 📚 Arquivos Modificados

- ✅ `core/models.py` - Adicionado método `calcular_metricas()` e override `save()`
- ✅ `core/views.py` - Filtros por `processado=True` em todas as views
- ✅ `core/management/commands/reprocessar_documentos.py` - Comando para reprocessar (novo)
