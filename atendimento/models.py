from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Cliente:
    id: int
    nome: str
    telefone: str
    prioridade: bool = False
    ativo: bool = True

    def to_dict(self) -> dict:
        return asdict(self)

    @staticmethod
    def from_dict(dados: dict) -> "Cliente":
        return Cliente(
            id=int(dados["id"]),
            nome=str(dados["nome"]),
            telefone=str(dados["telefone"]),
            prioridade=bool(dados.get("prioridade", False)),
            ativo=bool(dados.get("ativo", True)),
        )


@dataclass
class Atendente:
    id: int
    nome: str
    ocupado: bool = False

    def to_dict(self) -> dict:
        return asdict(self)

    @staticmethod
    def from_dict(dados: dict) -> "Atendente":
        return Atendente(
            id=int(dados["id"]),
            nome=str(dados["nome"]),
            ocupado=bool(dados.get("ocupado", False)),
        )


@dataclass
class AtendimentoAberto:
    id: int
    cliente_id: int
    entrada: str
    prioridade: bool

    def to_dict(self) -> dict:
        return asdict(self)

    @staticmethod
    def from_dict(dados: dict) -> "AtendimentoAberto":
        return AtendimentoAberto(
            id=int(dados["id"]),
            cliente_id=int(dados["cliente_id"]),
            entrada=str(dados["entrada"]),
            prioridade=bool(dados.get("prioridade", False)),
        )


@dataclass
class AtendimentoEmAndamento:
    id: int
    cliente_id: int
    atendente_id: int
    entrada: str
    inicio: str
    prioridade: bool

    def to_dict(self) -> dict:
        return asdict(self)

    @staticmethod
    def from_dict(dados: dict) -> "AtendimentoEmAndamento":
        return AtendimentoEmAndamento(
            id=int(dados["id"]),
            cliente_id=int(dados["cliente_id"]),
            atendente_id=int(dados["atendente_id"]),
            entrada=str(dados["entrada"]),
            inicio=str(dados["inicio"]),
            prioridade=bool(dados.get("prioridade", False)),
        )


@dataclass
class RegistroAtendimento:
    id: int
    cliente_id: int
    atendente_id: int
    data: str
    entrada: str
    inicio: str
    fim: str
    duracao_minutos: float
    espera_minutos: float
    prioridade: bool

    def to_dict(self) -> dict:
        return asdict(self)

    @staticmethod
    def from_dict(dados: dict) -> "RegistroAtendimento":
        return RegistroAtendimento(
            id=int(dados["id"]),
            cliente_id=int(dados["cliente_id"]),
            atendente_id=int(dados["atendente_id"]),
            data=str(dados["data"]),
            entrada=str(dados["entrada"]),
            inicio=str(dados["inicio"]),
            fim=str(dados["fim"]),
            duracao_minutos=float(dados["duracao_minutos"]),
            espera_minutos=float(dados.get("espera_minutos", 0)),
            prioridade=bool(dados.get("prioridade", False)),
        )


def agora_iso() -> str:
    return datetime.now().replace(microsecond=0).isoformat()


def minutos_entre(inicio: str, fim: Optional[str] = None) -> float:
    inicio_dt = datetime.fromisoformat(inicio)
    fim_dt = datetime.fromisoformat(fim or agora_iso())
    return round((fim_dt - inicio_dt).total_seconds() / 60, 2)
