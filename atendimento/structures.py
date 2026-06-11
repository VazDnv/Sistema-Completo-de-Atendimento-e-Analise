from collections import deque
from dataclasses import dataclass
from typing import Any, Callable, Iterable, Optional


class Fila:
    def __init__(self, itens: Optional[Iterable[Any]] = None):
        self._itens = deque(itens or [])

    def entrar(self, item: Any) -> None:
        self._itens.append(item)

    def sair(self) -> Any:
        if self.vazia():
            raise IndexError("Fila vazia.")
        return self._itens.popleft()

    def vazia(self) -> bool:
        return not self._itens

    def listar(self) -> list:
        return list(self._itens)

    def remover_por(self, predicado: Callable[[Any], bool]) -> list:
        removidos = []
        mantidos = deque()
        while self._itens:
            item = self._itens.popleft()
            if predicado(item):
                removidos.append(item)
            else:
                mantidos.append(item)
        self._itens = mantidos
        return removidos


class Pilha:
    def __init__(self):
        self._itens = []

    def empilhar(self, item: Any) -> None:
        self._itens.append(item)

    def desempilhar(self) -> Any:
        if self.vazia():
            raise IndexError("Pilha vazia.")
        return self._itens.pop()

    def vazia(self) -> bool:
        return not self._itens


@dataclass
class NoCliente:
    cliente_id: int
    proximo: Optional["NoCliente"] = None


class ListaClientesAtivos:
    def __init__(self):
        self.inicio: Optional[NoCliente] = None

    def inserir(self, cliente_id: int) -> None:
        if self.contem(cliente_id):
            return
        novo = NoCliente(cliente_id=cliente_id, proximo=self.inicio)
        self.inicio = novo

    def remover(self, cliente_id: int) -> bool:
        anterior = None
        atual = self.inicio
        while atual:
            if atual.cliente_id == cliente_id:
                if anterior:
                    anterior.proximo = atual.proximo
                else:
                    self.inicio = atual.proximo
                return True
            anterior = atual
            atual = atual.proximo
        return False

    def contem(self, cliente_id: int) -> bool:
        atual = self.inicio
        while atual:
            if atual.cliente_id == cliente_id:
                return True
            atual = atual.proximo
        return False

    def listar(self) -> list[int]:
        ids = []
        atual = self.inicio
        while atual:
            ids.append(atual.cliente_id)
            atual = atual.proximo
        return ids


def busca_binaria_recursiva(clientes: list, cliente_id: int, inicio: int = 0,
                            fim: Optional[int] = None):
    if fim is None:
        fim = len(clientes) - 1
    if inicio > fim:
        return None
    meio = (inicio + fim) // 2
    if clientes[meio].id == cliente_id:
        return clientes[meio]
    if cliente_id < clientes[meio].id:
        return busca_binaria_recursiva(clientes, cliente_id, inicio, meio - 1)
    return busca_binaria_recursiva(clientes, cliente_id, meio + 1, fim)


def insertion_sort_por_chave(itens: list, chave: Callable[[Any], Any],
                             reverso: bool = False) -> list:
    ordenados = itens[:]
    for i in range(1, len(ordenados)):
        atual = ordenados[i]
        j = i - 1
        if reverso:
            while j >= 0 and chave(ordenados[j]) < chave(atual):
                ordenados[j + 1] = ordenados[j]
                j -= 1
        else:
            while j >= 0 and chave(ordenados[j]) > chave(atual):
                ordenados[j + 1] = ordenados[j]
                j -= 1
        ordenados[j + 1] = atual
    return ordenados
