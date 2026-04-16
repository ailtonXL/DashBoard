from django.shortcuts import render, redirect
from .forms import AtestadoForm
from .models import Atestado
from django.db.models import Avg
import json


def dashboard(request):
    atestados = Atestado.objects.all()

    labels = [a.nome for a in atestados]
    values = [a.absenteismo for a in atestados]

    return render(request, "dashboard.html", {
        "labels": json.dumps(labels),
        "values": json.dumps(values),
    })


def administracao(request):
    atestados = Atestado.objects.all()

    total_atestados = atestados.count()

    # absenteísmo médio do mês
    absenteismo_medio = atestados.aggregate(media=Avg("absenteismo"))["media"] or 0

    return render(request, "administracao.html", {
        "total_atestados": total_atestados,
        "absenteismo_medio": round(absenteismo_medio, 2),
    })


def atestados(request):
    if request.method == "POST":
        form = AtestadoForm(request.POST, request.FILES)

        if form.is_valid():
            form.save()
            return redirect("atestados")
    else:
        form = AtestadoForm()

    return render(request, "atestado.html", {"form": form})


def contratos(request):
    return render(request, "contratos.html")


def gerencia(request):
    return render(request, "gerencia.html")


def logistica(request):
    return render(request, "logistica.html")


def manutencao(request):
    return render(request, "manutencao.html")


def meio_ambiente(request):
    return render(request, "meio_ambiente.html")


def operacoes(request):
    return render(request, "operacoes.html")


def qualidade_processos(request):
    return render(request, "qualidade_processos.html")


def saude_seguranca(request):
    return render(request, "saude_seguranca.html")


def suprimentos(request):
    return render(request, "suprimentos.html")