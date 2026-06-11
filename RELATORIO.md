# Relatorio tecnico

## Objetivo

O projeto implementa um sistema de atendimento para uma clinica ou central de atendimento, com cadastro, filas, historico, relatorios e persistencia em arquivo.

## Estruturas usadas

| Estrutura | Onde aparece | Motivo | Big-O principal |
|---|---|---|---|
| Vetor ordenado | `self.clientes` | Busca rapida por id | Busca binaria O(log n), insercao com reordenacao O(n log n) |
| Vetor nao ordenado | `self.clientes_temporarios` | Cadastro temporario e demonstracao de vetor simples | Insercao O(1) |
| Fila comum | `Fila` em `structures.py` | Atendimento normal por ordem de chegada | Entrar O(1), sair O(1) |
| Fila de prioridade | Outra instancia de `Fila` | Prioritarios ficam antes da fila comum | Entrar O(1), sair O(1) |
| Pilha | `desfazer_finalizacao` | Desfaz a ultima finalizacao | Empilhar O(1), desempilhar O(1) |
| Lista encadeada | `ListaClientesAtivos` | Mantem ids de clientes ativos e permite remocao sem deslocar vetor | Inserir O(1), buscar/remover O(n) |
| Ordenacao | `insertion_sort_por_chave` | Ordena relatorios, como top clientes e duracao | O(n²) |
| Recursao | `busca_binaria_recursiva` | Busca em vetor ordenado | O(log n) |

## Decisoes de projeto

A camada de regras fica em `service.py`, separada da interface de terminal (`cli.py`) e da persistencia (`storage.py`). Isso facilita testes e manutencao. O arquivo JSON foi escolhido por ser simples, legivel e suficiente para o tamanho do projeto.

Foram usadas duas filas: uma para prioridade e outra comum. Assim, clientes prioritarios sempre sao chamados primeiro, mas a ordem de chegada dentro de cada grupo continua correta.

O desfazer usa pilha porque a regra pede a reversao da ultima finalizacao. Como a ultima acao e sempre a primeira a ser desfeita, o comportamento LIFO e adequado.

## Relatorios

O sistema calcula tempo medio de atendimento, filtra historico por data, lista top 5 clientes mais atendidos, ordena atendimentos por duracao e exporta CSV.

## Tratamento de erros

Entradas invalidas do menu sao tratadas. As regras de negocio levantam `ErroRegraNegocio`, exibida de forma amigavel na interface.

## Testes

Os testes cobrem:

- prioridade antes da fila comum;
- busca binaria por id;
- finalizacao e desfazer com pilha;
- bloqueio de inativacao com atendimento aberto;
- relatorios basicos.
