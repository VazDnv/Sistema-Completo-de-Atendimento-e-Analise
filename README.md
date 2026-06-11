# Sistema Completo de Atendimento e Analise

Projeto em Python para gerenciamento de atendimentos em uma clinica ou central de atendimento. O sistema possui cadastro de clientes e atendentes, fila comum, fila de prioridade, chamada, finalizacao, historico, relatorios, exportacao CSV e busca rapida por cliente.

## Como executar

```bash
python main.py
```

O sistema usa apenas a biblioteca padrao do Python. O arquivo `requirements.txt` existe para cumprir o padrao de entrega, mas nao exige instalacoes.

## Como executar os testes

```bash
python -B -m unittest
```

## Funcionalidades

- Cadastro de clientes com id, nome, telefone, prioridade e status ativo.
- Cadastro de atendentes.
- Abertura de atendimento com entrada em fila.
- Fila de prioridade e fila comum.
- Chamada do proximo atendimento, sempre priorizando clientes prioritarios e mantendo ordem de chegada.
- Finalizacao com data, duracao, espera e atendente.
- Historico por cliente.
- Desfazer ultima finalizacao usando pilha.
- Marcacao e remocao de clientes inativos usando lista encadeada.
- Relatorio de tempo medio.
- Filtro por data.
- Top 5 clientes mais atendidos.
- Alertas de espera alta.
- Exportacao CSV.
- Busca rapida por cliente usando vetor ordenado e busca binaria recursiva.

## Organizacao

```text
atendimento/
  cli.py          Interface de terminal
  models.py       Entidades do sistema
  reports.py      Relatorios, filtros, exportacao CSV
  service.py      Regras de negocio
  storage.py      Persistencia em JSON
  structures.py   Filas, pilha, lista encadeada, busca e ordenacao
data/
  dados.json      Dados de exemplo
tests/
  test_service.py Testes unitarios basicos
main.py           Ponto de entrada
RELATORIO.md      Explicacao tecnica
```

## Persistencia

Os dados ficam em `data/dados.json`. Quando o menu e utilizado, o sistema salva automaticamente cadastros, filas, atendimentos em andamento e historico.

## Regras de negocio implementadas

- Cliente prioritario e chamado antes da fila comum.
- Dentro de cada fila, a ordem de chegada e preservada.
- Atendente nao pode chamar novo cliente se ja estiver ocupado.
- Nao e permitido finalizar atendimento sem atendimento em andamento.
- Nao e permitido inativar cliente com atendimento aberto.
- Cliente nao pode ter dois atendimentos abertos simultaneamente.
