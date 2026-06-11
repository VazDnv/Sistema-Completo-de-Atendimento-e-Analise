import tempfile
import unittest
from pathlib import Path

from atendimento.reports import tempo_medio, top_clientes_mais_atendidos
from atendimento.service import ErroRegraNegocio, SistemaAtendimento
from atendimento.storage import RepositorioArquivo


class TestSistemaAtendimento(unittest.TestCase):
    def criar_sistema(self):
        temp = tempfile.TemporaryDirectory()
        caminho = Path(temp.name) / "dados.json"
        sistema = SistemaAtendimento(RepositorioArquivo(str(caminho)))
        self.addCleanup(temp.cleanup)
        return sistema

    def test_prioridade_e_chamada_antes_da_fila_comum(self):
        sistema = self.criar_sistema()
        sistema.cadastrar_cliente(2, "Comum", "2222", False)
        sistema.cadastrar_cliente(1, "Prioritario", "1111", True)
        sistema.cadastrar_atendente(1, "Atendente")

        sistema.abrir_atendimento(2)
        sistema.abrir_atendimento(1)
        chamado = sistema.chamar_proximo(1)

        self.assertEqual(chamado.cliente_id, 1)

    def test_busca_binaria_encontra_cliente_por_id(self):
        sistema = self.criar_sistema()
        sistema.cadastrar_cliente(10, "Dez", "1010", False)
        sistema.cadastrar_cliente(5, "Cinco", "5555", False)

        cliente = sistema.buscar_cliente(5)

        self.assertIsNotNone(cliente)
        self.assertEqual(cliente.nome, "Cinco")

    def test_finalizar_e_desfazer_usando_pilha(self):
        sistema = self.criar_sistema()
        sistema.cadastrar_cliente(1, "Ana", "1111", False)
        sistema.cadastrar_atendente(1, "Mario")
        sistema.abrir_atendimento(1)
        sistema.chamar_proximo(1)

        registro = sistema.finalizar_atendimento(1)
        restaurado = sistema.desfazer_ultima_finalizacao()

        self.assertEqual(registro.id, restaurado.id)
        self.assertEqual(len(sistema.historico), 0)
        self.assertEqual(len(sistema.em_andamento), 1)

    def test_nao_remove_cliente_com_atendimento_aberto(self):
        sistema = self.criar_sistema()
        sistema.cadastrar_cliente(1, "Ana", "1111", False)
        sistema.abrir_atendimento(1)

        with self.assertRaises(ErroRegraNegocio):
            sistema.marcar_cliente_inativo(1)

    def test_relatorios_basicos(self):
        sistema = self.criar_sistema()
        sistema.cadastrar_cliente(1, "Ana", "1111", False)
        sistema.cadastrar_atendente(1, "Mario")
        sistema.abrir_atendimento(1)
        sistema.chamar_proximo(1)
        sistema.finalizar_atendimento(1)

        self.assertGreaterEqual(tempo_medio(sistema.historico), 0)
        self.assertEqual(top_clientes_mais_atendidos(sistema.historico)[0][0], 1)


if __name__ == "__main__":
    unittest.main()
