from atendimento.reports import (
    alertas_espera_alta,
    exportar_csv,
    filtrar_por_data,
    tempo_medio,
    top_clientes_mais_atendidos,
)
from atendimento.service import ErroRegraNegocio, SistemaAtendimento
from atendimento.storage import RepositorioArquivo


def executar_menu() -> None:
    sistema = SistemaAtendimento(RepositorioArquivo())
    opcoes = {
        "1": cadastrar_cliente,
        "2": cadastrar_atendente,
        "3": abrir_atendimento,
        "4": chamar_proximo,
        "5": finalizar_atendimento,
        "6": historico_cliente,
        "7": desfazer_finalizacao,
        "8": remover_inativos,
        "9": relatorios,
        "10": buscar_cliente,
        "0": sair,
    }
    while True:
        print("\n=== Sistema de Atendimento ===")
        print("1. Cadastrar cliente")
        print("2. Cadastrar atendente")
        print("3. Abrir atendimento")
        print("4. Chamar proximo")
        print("5. Finalizar atendimento")
        print("6. Historico por cliente")
        print("7. Desfazer ultima finalizacao")
        print("8. Remover clientes inativos")
        print("9. Relatorios")
        print("10. Busca rapida por cliente")
        print("0. Sair")
        escolha = input("Escolha: ").strip()
        acao = opcoes.get(escolha)
        if not acao:
            print("Opcao invalida.")
            continue
        try:
            if acao(sistema):
                break
        except ErroRegraNegocio as erro:
            print(f"Erro: {erro}")
        except ValueError:
            print("Erro: informe numeros validos.")


def cadastrar_cliente(sistema):
    cliente = sistema.cadastrar_cliente(
        ler_int("Id: "),
        input("Nome: "),
        input("Telefone: "),
        ler_bool("Prioridade? (s/n): "),
    )
    print(f"Cliente cadastrado: {cliente.nome}")


def cadastrar_atendente(sistema):
    atendente = sistema.cadastrar_atendente(ler_int("Id: "), input("Nome: "))
    print(f"Atendente cadastrado: {atendente.nome}")


def abrir_atendimento(sistema):
    atendimento = sistema.abrir_atendimento(ler_int("Id do cliente: "))
    print(f"Atendimento aberto: {atendimento.id}")


def chamar_proximo(sistema):
    atendimento = sistema.chamar_proximo(ler_int("Id do atendente: "))
    print(
        f"Cliente {atendimento.cliente_id} chamado pelo atendente "
        f"{atendimento.atendente_id}."
    )


def finalizar_atendimento(sistema):
    registro = sistema.finalizar_atendimento(ler_int("Id do atendente: "))
    print(f"Atendimento finalizado. Duracao: {registro.duracao_minutos} min.")


def historico_cliente(sistema):
    registros = sistema.historico_por_cliente(ler_int("Id do cliente: "))
    if not registros:
        print("Cliente sem historico.")
    for registro in registros:
        print(
            f"Atendimento {registro.id} em {registro.data}: "
            f"{registro.duracao_minutos} min."
        )


def desfazer_finalizacao(sistema):
    atendimento = sistema.desfazer_ultima_finalizacao()
    print(f"Finalizacao desfeita. Atendimento {atendimento.id} voltou.")


def remover_inativos(sistema):
    removidos = sistema.remover_clientes_inativos()
    print(f"Clientes removidos: {len(removidos)}")


def relatorios(sistema):
    data_inicio = input("Data inicial (AAAA-MM-DD ou vazio): ").strip() or None
    data_fim = input("Data final (AAAA-MM-DD ou vazio): ").strip() or None
    registros = filtrar_por_data(sistema.historico, data_inicio, data_fim)
    print(f"Tempo medio: {tempo_medio(registros)} min.")
    print("Top 5 clientes:")
    for cliente_id, total in top_clientes_mais_atendidos(registros):
        print(f"Cliente {cliente_id}: {total} atendimento(s)")
    for alerta in alertas_espera_alta(sistema.listar_filas()):
        print(f"Alerta: {alerta}")
    if ler_bool("Exportar CSV? (s/n): "):
        caminho = exportar_csv(registros, "exports/relatorio_atendimentos.csv")
        print(f"CSV exportado em: {caminho}")


def buscar_cliente(sistema):
    cliente = sistema.buscar_cliente(ler_int("Id do cliente: "))
    if cliente:
        status = "ativo" if cliente.ativo else "inativo"
        print(f"{cliente.id} - {cliente.nome} - {status}")
    else:
        print("Cliente nao encontrado.")


def sair(_sistema):
    print("Encerrando.")
    return True


def ler_int(mensagem: str) -> int:
    return int(input(mensagem).strip())


def ler_bool(mensagem: str) -> bool:
    valor = input(mensagem).strip().lower()
    return valor in {"s", "sim", "y", "yes"}
