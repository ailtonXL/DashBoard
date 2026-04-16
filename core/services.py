def calcular_dias_atestado(atestado):
    inicio = atestado.data_inicio
    fim = atestado.data_fim

    return max((fim - inicio).days + 1, 0)


def calcular_absenteismo(dias_ausentes, dias_uteis):
    if dias_uteis <= 0:
        return 0

    return round((dias_ausentes / dias_uteis) * 100, 2)


def atualizar_absenteismo(atestado, dias_uteis_mes=22):
    dias_ausentes = calcular_dias_atestado(atestado)
    absenteismo = calcular_absenteismo(dias_ausentes, dias_uteis_mes)

    atestado.dias_afastado = dias_ausentes
    atestado.absenteismo = absenteismo
    atestado.processado = True
    atestado.save()

    return absenteismo