from django.urls import path
from . import views

urlpatterns = [
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("", views.dashboard, name="dashboard"),

    path("administracao/", views.administracao, name="administracao"),
    path("gerencia/", views.gerencia, name="gerencia"),
    path("logistica/", views.logistica, name="logistica"),
    path("manutencao/", views.manutencao, name="manutencao"),
    path("meio-ambiente/", views.meio_ambiente, name="meio_ambiente"),
    path("operacoes/", views.operacoes, name="operacoes"),
    path("qualidade-processos/", views.qualidade_processos, name="qualidade_processos"),
    path("saude-seguranca/", views.saude_seguranca, name="saude_seguranca"),
    path("suprimentos/", views.suprimentos, name="suprimentos"),

    # DOCUMENTOS (novo nome)
    path("documentos/", views.atestados, name="documentos"),
    # ATESTADOS (compatibilidade)
    path("atestados/", views.atestados, name="atestados"),

    # CONTRATOS
    path("contratos/", views.contratos, name="contratos"),
]
