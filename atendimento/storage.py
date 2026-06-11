import json
from pathlib import Path

from atendimento.models import (
    Atendente,
    AtendimentoAberto,
    AtendimentoEmAndamento,
    Cliente,
    RegistroAtendimento,
)


class RepositorioArquivo:
    def __init__(self, caminho: str = "data/dados.json"):
        self.caminho = Path(caminho)

    def carregar(self) -> dict:
        if not self.caminho.exists():
            return self._dados_vazios()
        with self.caminho.open("r", encoding="utf-8") as arquivo:
            dados = json.load(arquivo)
        return {
            "clientes": [
                Cliente.from_dict(item)
                for item in dados.get("clientes", [])
            ],
            "atendentes": [
                Atendente.from_dict(item)
                for item in dados.get("atendentes", [])
            ],
            "fila_prioridade": [
                AtendimentoAberto.from_dict(item)
                for item in dados.get("fila_prioridade", [])
            ],
            "fila_comum": [
                AtendimentoAberto.from_dict(item)
                for item in dados.get("fila_comum", [])
            ],
            "em_andamento": [
                AtendimentoEmAndamento.from_dict(item)
                for item in dados.get("em_andamento", [])
            ],
            "historico": [
                RegistroAtendimento.from_dict(item)
                for item in dados.get("historico", [])
            ],
            "proximo_atendimento_id": int(
                dados.get("proximo_atendimento_id", 1)
            ),
        }

    def salvar(self, dados: dict) -> None:
        self.caminho.parent.mkdir(parents=True, exist_ok=True)
        serializado = {
            "clientes": [item.to_dict() for item in dados["clientes"]],
            "atendentes": [item.to_dict() for item in dados["atendentes"]],
            "fila_prioridade": [
                item.to_dict() for item in dados["fila_prioridade"]
            ],
            "fila_comum": [item.to_dict() for item in dados["fila_comum"]],
            "em_andamento": [
                item.to_dict() for item in dados["em_andamento"]
            ],
            "historico": [item.to_dict() for item in dados["historico"]],
            "proximo_atendimento_id": dados["proximo_atendimento_id"],
        }
        with self.caminho.open("w", encoding="utf-8") as arquivo:
            json.dump(serializado, arquivo, indent=2, ensure_ascii=False)

    @staticmethod
    def _dados_vazios() -> dict:
        return {
            "clientes": [],
            "atendentes": [],
            "fila_prioridade": [],
            "fila_comum": [],
            "em_andamento": [],
            "historico": [],
            "proximo_atendimento_id": 1,
        }
