import csv
from collections import Counter
from pathlib import Path
from typing import Optional

from atendimento.models import RegistroAtendimento, minutos_entre
from atendimento.structures import insertion_sort_por_chave


def filtrar_por_data(historico: list[RegistroAtendimento],
                     data_inicio: Optional[str] = None,
                     data_fim: Optional[str] = None) -> list[RegistroAtendimento]:
    registros = historico
    if data_inicio:
        registros = [r for r in registros if r.data >= data_inicio]
    if data_fim:
        registros = [r for r in registros if r.data <= data_fim]
    return registros


def tempo_medio(historico: list[RegistroAtendimento]) -> float:
    if not historico:
        return 0.0
    total = sum(registro.duracao_minutos for registro in historico)
    return round(total / len(historico), 2)


def top_clientes_mais_atendidos(historico: list[RegistroAtendimento],
                                limite: int = 5) -> list[tuple[int, int]]:
    contagem = Counter(registro.cliente_id for registro in historico)
    pares = list(contagem.items())
    return insertion_sort_por_chave(pares, lambda item: item[1], True)[:limite]


def atendimentos_ordenados_por_duracao(
    historico: list[RegistroAtendimento],
) -> list[RegistroAtendimento]:
    return insertion_sort_por_chave(
        historico,
        lambda registro: registro.duracao_minutos,
        True,
    )


def alertas_espera_alta(filas: dict, limite_minutos: float = 20) -> list[str]:
    alertas = []
    for nome_fila, atendimentos in filas.items():
        for atendimento in atendimentos:
            espera = minutos_entre(atendimento.entrada)
            if espera >= limite_minutos:
                alertas.append(
                    f"Atendimento {atendimento.id} na fila {nome_fila} "
                    f"aguarda ha {espera} minutos."
                )
    return alertas


def exportar_csv(historico: list[RegistroAtendimento], caminho: str) -> Path:
    destino = Path(caminho)
    destino.parent.mkdir(parents=True, exist_ok=True)
    campos = [
        "id",
        "cliente_id",
        "atendente_id",
        "data",
        "entrada",
        "inicio",
        "fim",
        "duracao_minutos",
        "espera_minutos",
        "prioridade",
    ]
    with destino.open("w", newline="", encoding="utf-8") as arquivo:
        escritor = csv.DictWriter(arquivo, fieldnames=campos)
        escritor.writeheader()
        for registro in historico:
            escritor.writerow(registro.to_dict())
    return destino
