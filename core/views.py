from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import AtestadoForm, LoginForm
from .models import Atestado, UsuarioComRole
from django.db.models import Avg, Sum
from django.db import models
import json
from functools import wraps
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils import timezone


@never_cache
@ensure_csrf_cookie
def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('dashboard')
    else:
        form = LoginForm()
    
    return render(request, 'login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('login')


def check_permission(required_role):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')
            
            try:
                user_role = request.user.role_profile
                if user_role.is_gerencia or user_role.role == required_role:
                    return view_func(request, *args, **kwargs)
                else:
                    messages.error(request, 'Você não tem permissão para acessar esta página.')
                    return redirect('dashboard')
            except UsuarioComRole.DoesNotExist:
                messages.error(request, 'Perfil de usuário não configurado.')
                return redirect('login')
        
        return wrapper
    return decorator


def build_area_context(area_nome, descricao, prioridade_titulos):
    # Considerar apenas documentos processados
    documentos = Atestado.objects.filter(processado=True).order_by('-created_at')
    
    # Total de documentos processados
    total_documentos = documentos.count()
    
    # Absenteismo médio (excluindo valores 0)
    docs_com_absenteismo = documentos.filter(absenteismo__gt=0)
    absenteismo_medio = docs_com_absenteismo.aggregate(media=Avg('absenteismo'))['media'] or 0

    # Documentos e dias do mês
    hoje = timezone.now().date()
    inicio_mes = hoje.replace(day=1)
    documentos_mes = documentos.filter(created_at__date__gte=inicio_mes).count()
    
    # Total de dias afastados no mês
    dias_afastados_mes = documentos.filter(created_at__date__gte=inicio_mes).aggregate(
        total=models.Sum('dias_afastado')
    )['total'] or 0

    # Últimos documentos processados
    ultimos_documentos = []
    for item in documentos[:6]:
        ultimos_documentos.append({
            'nome': item.nome,
            'empresa': item.empresa,
            'tipo': item.get_tipo_display(),
            'periodo': f"{item.data_inicio} ate {item.data_fim}",
            'dias': item.dias_afastado,
        })

    return {
        'area_nome': area_nome,
        'descricao': descricao,
        'indicadores': [
            {'titulo': 'Total de Documentos', 'valor': total_documentos},
            {'titulo': 'Documentos no Mes', 'valor': documentos_mes},
            {'titulo': 'Dias Afastados (Mes)', 'valor': dias_afastados_mes},
            {'titulo': 'Absenteismo Medio', 'valor': f"{round(absenteismo_medio, 2)}%"},
        ],
        'prioridades': prioridade_titulos,
        'ultimos_documentos': ultimos_documentos,
    }


@login_required(login_url='login')
def dashboard(request):
    # Considerar apenas documentos processados
    atestados = Atestado.objects.filter(processado=True).order_by('-absenteismo')

    nomes = [a.nome for a in atestados]
    absenteismos = [a.absenteismo for a in atestados]

    # Dados para gráfico geral: absenteísmo total vs horas trabalhadas
    total_absenteismo = sum(absenteismos)
    # Base: 22 dias úteis * quantidade de documentos, em %
    total_documentos = len(absenteismos)
    absenteismo_medio = round(total_absenteismo / total_documentos, 2) if total_documentos > 0 else 0
    presenca_media = round(100 - absenteismo_medio, 2)

    return render(request, "dashboard.html", {
        "nomes_json": json.dumps(nomes),
        "absenteismos_json": json.dumps(absenteismos),
        "absenteismo_medio": absenteismo_medio,
        "presenca_media": presenca_media,
    })


@login_required(login_url='login')
@check_permission('admin')
def administracao(request):
    # Considerar apenas documentos processados
    atestados = Atestado.objects.filter(processado=True).order_by('-absenteismo')

    total_atestados = atestados.count()
    
    # Gerar dados para gráfico (top 10 com maior absenteísmo)
    labels = [a.nome for a in atestados[:10]]
    values = [a.absenteismo for a in atestados[:10]]

    # Absenteísmo médio apenas de documentos com absenteísmo > 0
    atestados_com_absenteismo = atestados.filter(absenteismo__gt=0)
    absenteismo_medio = atestados_com_absenteismo.aggregate(media=Avg("absenteismo"))["media"] or 0
    
    # Total de dias afastados
    total_dias_afastados = atestados.aggregate(total=Sum('dias_afastado'))['total'] or 0

    return render(request, "administracao.html", {
        "total_atestados": total_atestados,
        "absenteismo": round(absenteismo_medio, 2),
        "labels_json": json.dumps(labels),
        "values_json": json.dumps(values),
        "total_dias_afastados": total_dias_afastados,
    })


@login_required(login_url='login')
@check_permission('admin')
def buscar_documentos(request):
    """Buscar documentos por nome do funcionário e acessar arquivos."""
    query = request.GET.get('q', '').strip()
    documentos = []
    
    if query:
        # Buscar documentos que contenham o nome pesquisado
        documentos = Atestado.objects.filter(
            nome__icontains=query,
            processado=True
        ).order_by('-created_at')
    
    # Preparar dados para exibição
    docs_com_arquivo = []
    for doc in documentos:
        docs_com_arquivo.append({
            'id': doc.id,
            'nome': doc.nome,
            'empresa': doc.empresa,
            'tipo': doc.get_tipo_display(),
            'data_inicio': doc.data_inicio,
            'data_fim': doc.data_fim,
            'dias_afastado': doc.dias_afastado,
            'absenteismo': doc.absenteismo,
            'arquivo_url': doc.arquivo.url if doc.arquivo else None,
            'arquivo_nome': doc.arquivo.name.split('/')[-1] if doc.arquivo else 'Sem arquivo',
            'created_at': doc.created_at,
        })
    
    return render(request, "administracao.html", {
        "aba_ativa": "busca",
        "query": query,
        "documentos_encontrados": docs_com_arquivo,
        "total_encontrados": len(docs_com_arquivo),
        "total_atestados": 0,
        "absenteismo": 0,
        "labels_json": json.dumps([]),
        "values_json": json.dumps([]),
    })


@login_required(login_url='login')
@check_permission('admin')
@never_cache
@ensure_csrf_cookie
def atestados(request):
    if request.method == "POST":
        form = AtestadoForm(request.POST, request.FILES)

        if form.is_valid():
            documento = form.save()
            # Os cálculos são feitos automaticamente no save() do modelo
            return redirect("documentos")
    else:
        form = AtestadoForm()

    return render(request, "atestado.html", {"form": form})


@login_required(login_url='login')
@check_permission('admin')
def contratos(request):
    context = build_area_context(
        'Contratos',
        'Controle de contratos e fornecedores criticos.',
        [
            'Renovacoes com vencimento em 30 dias',
            'Conferir clausulas de SLA por fornecedor',
            'Validar documentacao de compliance',
        ],
    )
    return render(request, "area.html", context)


@login_required(login_url='login')
@check_permission('gerencia')
def gerencia(request):
    context = build_area_context(
        'Gerencia',
        'Visao executiva com foco em performance e direcionamento.',
        [
            'Alinhar metas semanais por time',
            'Acompanhar absenteismo critico',
            'Priorizar aprovacoes pendentes',
        ],
    )
    return render(request, "area.html", context)


@login_required(login_url='login')
@check_permission('logistica')
def logistica(request):
    context = build_area_context(
        'Logistica',
        'Acompanhamento de fluxos, distribuicao e disponibilidade operacional.',
        [
            'Monitorar gargalos de distribuicao',
            'Atualizar janelas de entrega',
            'Conferir cobertura de equipes por turno',
        ],
    )
    return render(request, "area.html", context)


@login_required(login_url='login')
@check_permission('manutencao')
def manutencao(request):
    context = build_area_context(
        'Manutencao',
        'Painel de suporte para disponibilidade de ativos e manutencoes.',
        [
            'Fechar ordens em atraso',
            'Programar preventivas da semana',
            'Escalonar falhas recorrentes',
        ],
    )
    return render(request, "area.html", context)


@login_required(login_url='login')
@check_permission('meio_ambiente')
def meio_ambiente(request):
    context = build_area_context(
        'Meio Ambiente',
        'Indicadores de conformidade ambiental e sustentabilidade.',
        [
            'Atualizar controles de residuos',
            'Conferir pendencias de auditoria',
            'Reforcar acoes de consumo consciente',
        ],
    )
    return render(request, "area.html", context)


@login_required(login_url='login')
@check_permission('operacoes')
def operacoes(request):
    context = build_area_context(
        'Operacoes',
        'Acompanhamento da rotina operacional e produtividade diaria.',
        [
            'Reduzir filas de atendimento',
            'Garantir cobertura de turnos',
            'Revisar indicadores abaixo da meta',
        ],
    )
    return render(request, "area.html", context)


@login_required(login_url='login')
@check_permission('qualidade')
def qualidade_processos(request):
    context = build_area_context(
        'Qualidade e Processos',
        'Controle de padroes, nao conformidades e melhoria continua.',
        [
            'Tratar nao conformidades abertas',
            'Atualizar procedimentos operacionais',
            'Publicar plano de melhoria mensal',
        ],
    )
    return render(request, "area.html", context)


@login_required(login_url='login')
@check_permission('saude')
def saude_seguranca(request):
    context = build_area_context(
        'Saude e Seguranca',
        'Gestao preventiva de riscos e conformidade de seguranca do trabalho.',
        [
            'Auditar uso de EPIs por setor',
            'Atualizar mapa de riscos',
            'Registrar DDS semanal',
        ],
    )
    return render(request, "area.html", context)


@login_required(login_url='login')
@check_permission('suprimentos')
def suprimentos(request):
    context = build_area_context(
        'Suprimentos',
        'Planejamento de compras, estoque e abastecimento interno.',
        [
            'Repor itens criticos do estoque',
            'Atualizar cotacoes pendentes',
            'Acompanhar lead time de fornecedores',
        ],
    )
    return render(request, "area.html", context)
