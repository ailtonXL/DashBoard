from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import SetPasswordForm
from django.contrib import messages
from .forms import AtestadoForm, HorimetroRegistroForm, LoginForm
from .models import Atestado, HorimetroRegistro, UsuarioComRole
from django.db.models import Avg, Sum, Q
from django.db import models
import json
from functools import wraps
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils import timezone


def get_user_profile(user):
    try:
        return user.role_profile
    except UsuarioComRole.DoesNotExist:
        return None


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

            user_role = get_user_profile(request.user)
            if user_role is None:
                messages.error(request, 'Perfil de usuário não configurado.')
                return redirect('login')

            if user_role.precisa_alterar_senha:
                return redirect('alterar_senha_primeiro_acesso')

            if user_role.is_gerencia or user_role.role == required_role:
                return view_func(request, *args, **kwargs)

            messages.error(request, 'Você não tem permissão para acessar esta página.')
            return redirect('dashboard')
        
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
    profile = get_user_profile(request.user)
    if profile and profile.precisa_alterar_senha:
        return redirect('alterar_senha_primeiro_acesso')

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
        "profile": profile,
        "nomes_json": json.dumps(nomes),
        "absenteismos_json": json.dumps(absenteismos),
        "absenteismo_medio": absenteismo_medio,
        "presenca_media": presenca_media,
    })


@login_required(login_url='login')
@never_cache
@ensure_csrf_cookie
def alterar_senha_primeiro_acesso(request):
    role_profile = get_user_profile(request.user)
    if role_profile is None:
        messages.error(request, 'Perfil de usuário não configurado.')
        return redirect('login')

    if not role_profile.precisa_alterar_senha:
        return redirect('dashboard')

    if request.method == 'POST':
        form = SetPasswordForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)

            role_profile.precisa_alterar_senha = False
            role_profile.save(update_fields=['precisa_alterar_senha'])

            messages.success(request, 'Senha alterada com sucesso.')
            return redirect('dashboard')
    else:
        form = SetPasswordForm(user=request.user)

    return render(request, 'alterar_senha_primeiro_acesso.html', {'form': form})


@login_required(login_url='login')
def administracao(request):
    user_role = get_user_profile(request.user)
    if user_role is None:
        messages.error(request, 'Perfil de usuário não configurado.')
        return redirect('login')

    if not (user_role.is_gerencia or user_role.role in ['admin', 'saude']):
        messages.error(request, 'Você não tem permissão para acessar esta página.')
        return redirect('dashboard')

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
def buscar_documentos(request):
    """Buscar documentos por nome do funcionário e acessar arquivos."""
    user_role = get_user_profile(request.user)
    if user_role is None:
        messages.error(request, 'Perfil de usuário não configurado.')
        return redirect('login')

    if not (user_role.is_gerencia or user_role.role in ['admin', 'saude']):
        messages.error(request, 'Você não tem permissão para acessar esta página.')
        return redirect('dashboard')

    query = request.GET.get('q', '').strip()
    documentos = []
    
    if query:
        # Como o nome está criptografado no banco, filtramos em memória após descriptografar.
        base_qs = Atestado.objects.filter(processado=True).order_by('-created_at')
        query_lower = query.lower()
        documentos = [doc for doc in base_qs if query_lower in (doc.nome or '').lower()]
    
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


def build_sst_context():
    context = build_area_context(
        'Saude e Seguranca',
        'Gestao preventiva de riscos e conformidade de seguranca do trabalho.',
        [
            'Auditar uso de EPIs por setor',
            'Atualizar mapa de riscos',
            'Registrar DDS semanal',
        ],
    )
    context.update({
        'total_registros_horimetro': HorimetroRegistro.objects.count(),
    })
    return context


@login_required(login_url='login')
@check_permission('saude')
def saude_seguranca(request):
    context = build_sst_context()

    if request.method == 'POST':
        horimetro_form = HorimetroRegistroForm(request.POST)
        if horimetro_form.is_valid():
            horimetro_form.save()
            messages.success(request, 'Registro de horimetro salvo com sucesso.')
            return redirect('saude_seguranca')
    else:
        horimetro_form = HorimetroRegistroForm()

    registros = HorimetroRegistro.objects.all()
    filtro_tipo = request.GET.get('tipo', '').strip()
    filtro_nome = request.GET.get('nome', '').strip()
    filtro_veiculo = request.GET.get('veiculo', '').strip()
    filtro_placa = request.GET.get('placa', '').strip().upper().replace('-', '').replace(' ', '')
    filtro_data = request.GET.get('data', '').strip()

    # Compatibilidade com filtro legado "veiculo" e novo filtro unificado "nome".
    termo_nome = filtro_nome or filtro_veiculo

    if filtro_tipo in ['veiculo', 'maquina']:
        registros = registros.filter(tipo_registro=filtro_tipo)

    if termo_nome:
        if filtro_tipo == 'veiculo':
            registros = registros.filter(veiculo__icontains=termo_nome)
        elif filtro_tipo == 'maquina':
            registros = registros.filter(maquinario__icontains=termo_nome)
        else:
            registros = registros.filter(Q(veiculo__icontains=termo_nome) | Q(maquinario__icontains=termo_nome))
    if filtro_placa:
        registros = registros.filter(placa__icontains=filtro_placa)
    if filtro_data:
        registros = registros.filter(data_registro=filtro_data)

    context.update({
        'horimetro_form': horimetro_form,
        'horimetro_registros': registros[:20],
        'total_registros_horimetro': registros.count(),
        'filtros_horimetro': {
            'tipo': filtro_tipo,
            'nome': termo_nome,
            'veiculo': filtro_veiculo,
            'placa': request.GET.get('placa', '').strip(),
            'data': filtro_data,
        },
    })

    return render(request, "horimetro.html", context)


@login_required(login_url='login')
@check_permission('saude')
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
