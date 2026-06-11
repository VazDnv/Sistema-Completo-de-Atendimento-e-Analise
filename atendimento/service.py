import logging
from pathlib import Path

from atendimento.models import (
    Atendente,
    AtendimentoAberto,
    AtendimentoEmAndamento,
    Cliente,
    RegistroAtendimento,
    agora_iso,
    minutos_entre,
)
from atendimento.storage import RepositorioArquivo
from atendimento.structures import (
    Fila,
    ListaClientesAtivos,
    Pilha,
    busca_binaria_recursiva,
)


class ErroRegraNegocio(ValueError):
    pass


class SistemaAtendimento:
    def __init__(self, repositorio: RepositorioArquivo):
        self.repositorio = repositorio
        self.desfazer_finalizacao = Pilha()
        self.log = logging.getLogger("sistema_atendimento")
        self._configurar_logs()
        self._carregar()

    def _configurar_logs(self) -> None:
        Path("logs").mkdir(exist_ok=True)
        if not logging.getLogger("sistema_atendimento").handlers:
            logging.basicConfig(
                filename="logs/operacoes.log",
                level=logging.INFO,
                format="%(asctime)s - %(levelname)s - %(message)s",
            )

    def _carregar(self) -> None:
        dados = self.repositorio.carregar()
        self.clientes = sorted(dados["clientes"], key=lambda c: c.id)
        self.clientes_temporarios = dados["clientes"][:]
        self.atendentes = dados["atendentes"]
        self.fila_prioridade = Fila(dados["fila_prioridade"])
        self.fila_comum = Fila(dados["fila_comum"])
        self.em_andamento = dados["em_andamento"]
        self.historico = dados["historico"]
        self.proximo_atendimento_id = dados["proximo_atendimento_id"]
        self.clientes_ativos = ListaClientesAtivos()
        for cliente in self.clientes:
            if cliente.ativo:
                self.clientes_ativos.inserir(cliente.id)

    def salvar(self) -> None:
        self.repositorio.salvar({
            "clientes": self.clientes,
            "atendentes": self.atendentes,
            "fila_prioridade": self.fila_prioridade.listar(),
            "fila_comum": self.fila_comum.listar(),
            "em_andamento": self.em_andamento,
            "historico": self.historico,
            "proximo_atendimento_id": self.proximo_atendimento_id,
        })

    def cadastrar_cliente(self, cliente_id: int, nome: str, telefone: str,
                          prioridade: bool) -> Cliente:
        self._validar_id(cliente_id)
        if self.buscar_cliente(cliente_id):
            raise ErroRegraNegocio("Ja existe cliente com esse id.")
        cliente = Cliente(cliente_id, nome.strip(), telefone.strip(), prioridade)
        self.clientes.append(cliente)
        self.clientes = sorted(self.clientes, key=lambda c: c.id)
        self.clientes_temporarios.append(cliente)
        self.clientes_ativos.inserir(cliente.id)
        self.salvar()
        self.log.info("Cliente cadastrado: %s", cliente.id)
        return cliente

    def cadastrar_atendente(self, atendente_id: int, nome: str) -> Atendente:
        self._validar_id(atendente_id)
        if self._buscar_atendente(atendente_id):
            raise ErroRegraNegocio("Ja existe atendente com esse id.")
        atendente = Atendente(atendente_id, nome.strip())
        self.atendentes.append(atendente)
        self.salvar()
        self.log.info("Atendente cadastrado: %s", atendente.id)
        return atendente

    def abrir_atendimento(self, cliente_id: int) -> AtendimentoAberto:
        cliente = self._cliente_ativo(cliente_id)
        if self._cliente_tem_atendimento_aberto(cliente_id):
            raise ErroRegraNegocio("Cliente ja possui atendimento aberto.")
        atendimento = AtendimentoAberto(
            id=self.proximo_atendimento_id,
            cliente_id=cliente.id,
            entrada=agora_iso(),
            prioridade=cliente.prioridade,
        )
        self.proximo_atendimento_id += 1
        if cliente.prioridade:
            self.fila_prioridade.entrar(atendimento)
        else:
            self.fila_comum.entrar(atendimento)
        self.salvar()
        self.log.info("Atendimento aberto: %s", atendimento.id)
        return atendimento

    def chamar_proximo(self, atendente_id: int) -> AtendimentoEmAndamento:
        atendente = self._buscar_atendente(atendente_id)
        if not atendente:
            raise ErroRegraNegocio("Atendente nao encontrado.")
        if atendente.ocupado:
            raise ErroRegraNegocio("Atendente ja esta ocupado.")
        if self.fila_prioridade.vazia() and self.fila_comum.vazia():
            raise ErroRegraNegocio("Nao ha clientes na fila.")
        aberto = (
            self.fila_prioridade.sair()
            if not self.fila_prioridade.vazia()
            else self.fila_comum.sair()
        )
        atendente.ocupado = True
        atual = AtendimentoEmAndamento(
            id=aberto.id,
            cliente_id=aberto.cliente_id,
            atendente_id=atendente.id,
            entrada=aberto.entrada,
            inicio=agora_iso(),
            prioridade=aberto.prioridade,
        )
        self.em_andamento.append(atual)
        self.salvar()
        self.log.info("Atendimento chamado: %s", atual.id)
        return atual

    def finalizar_atendimento(self, atendente_id: int) -> RegistroAtendimento:
        atendimento = self._atendimento_por_atendente(atendente_id)
        if not atendimento:
            raise ErroRegraNegocio(
                "Nao ha atendimento em andamento para esse atendente."
            )
        fim = agora_iso()
        registro = RegistroAtendimento(
            id=atendimento.id,
            cliente_id=atendimento.cliente_id,
            atendente_id=atendimento.atendente_id,
            data=fim[:10],
            entrada=atendimento.entrada,
            inicio=atendimento.inicio,
            fim=fim,
            duracao_minutos=minutos_entre(atendimento.inicio, fim),
            espera_minutos=minutos_entre(atendimento.entrada, atendimento.inicio),
            prioridade=atendimento.prioridade,
        )
        self.em_andamento.remove(atendimento)
        atendente = self._buscar_atendente(atendente_id)
        atendente.ocupado = False
        self.historico.append(registro)
        self.desfazer_finalizacao.empilhar(registro)
        self.salvar()
        self.log.info("Atendimento finalizado: %s", registro.id)
        return registro

    def desfazer_ultima_finalizacao(self) -> AtendimentoEmAndamento:
        if self.desfazer_finalizacao.vazia():
            raise ErroRegraNegocio("Nao ha finalizacao para desfazer.")
        registro = self.desfazer_finalizacao.desempilhar()
        self.historico = [h for h in self.historico if h.id != registro.id]
        atendente = self._buscar_atendente(registro.atendente_id)
        if atendente and not atendente.ocupado:
            atendente.ocupado = True
        restaurado = AtendimentoEmAndamento(
            id=registro.id,
            cliente_id=registro.cliente_id,
            atendente_id=registro.atendente_id,
            entrada=registro.entrada,
            inicio=registro.inicio,
            prioridade=registro.prioridade,
        )
        self.em_andamento.append(restaurado)
        self.salvar()
        self.log.info("Finalizacao desfeita: %s", registro.id)
        return restaurado

    def remover_clientes_inativos(self) -> list[Cliente]:
        removidos = []
        for cliente in self.clientes:
            if not cliente.ativo and not self._cliente_tem_atendimento_aberto(
                cliente.id
            ):
                self.clientes_ativos.remover(cliente.id)
                removidos.append(cliente)
        self.clientes = [c for c in self.clientes if c not in removidos]
        self.salvar()
        self.log.info("Clientes inativos removidos: %s", len(removidos))
        return removidos

    def marcar_cliente_inativo(self, cliente_id: int) -> Cliente:
        cliente = self.buscar_cliente(cliente_id)
        if not cliente:
            raise ErroRegraNegocio("Cliente nao encontrado.")
        if self._cliente_tem_atendimento_aberto(cliente_id):
            raise ErroRegraNegocio(
                "Nao e permitido inativar cliente com atendimento aberto."
            )
        cliente.ativo = False
        self.salvar()
        return cliente

    def historico_por_cliente(self, cliente_id: int) -> list[RegistroAtendimento]:
        self._cliente_ativo_ou_existente(cliente_id)
        return [h for h in self.historico if h.cliente_id == cliente_id]

    def buscar_cliente(self, cliente_id: int):
        return busca_binaria_recursiva(self.clientes, cliente_id)

    def listar_filas(self) -> dict:
        return {
            "prioridade": self.fila_prioridade.listar(),
            "comum": self.fila_comum.listar(),
        }

    def _cliente_ativo(self, cliente_id: int) -> Cliente:
        cliente = self.buscar_cliente(cliente_id)
        if not cliente or not cliente.ativo:
            raise ErroRegraNegocio("Cliente nao encontrado ou inativo.")
        return cliente

    def _cliente_ativo_ou_existente(self, cliente_id: int) -> Cliente:
        cliente = self.buscar_cliente(cliente_id)
        if not cliente:
            raise ErroRegraNegocio("Cliente nao encontrado.")
        return cliente

    def _buscar_atendente(self, atendente_id: int):
        return next((a for a in self.atendentes if a.id == atendente_id), None)

    def _atendimento_por_atendente(self, atendente_id: int):
        return next(
            (a for a in self.em_andamento if a.atendente_id == atendente_id),
            None,
        )

    def _cliente_tem_atendimento_aberto(self, cliente_id: int) -> bool:
        em_fila = any(
            a.cliente_id == cliente_id
            for a in self.fila_prioridade.listar() + self.fila_comum.listar()
        )
        em_atendimento = any(
            a.cliente_id == cliente_id for a in self.em_andamento
        )
        return em_fila or em_atendimento

    @staticmethod
    def _validar_id(valor: int) -> None:
        if not isinstance(valor, int) or valor <= 0:
            raise ErroRegraNegocio("Id deve ser um numero inteiro positivo.")
