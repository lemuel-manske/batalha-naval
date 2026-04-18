# batalha-naval

Este repositório contém a implementação do jogo de batalha naval em Python, com foco em conceitos de teoria dos jogos, inteligência artificial e algoritmos de busca competitiva.

# Sobre o jogo

## Objetivo

Afundar todos os navios do adversário antes que ele afunde os seus.

## Preparação

Cada jogador possui:
- Um tabuleiro de mapeamento, onde posiciona seus navios
- Um tabuleiro de ataque, onde registra os ataques realizados

### Navios

Cada jogador possui os seguintes navios:
- 1 porta-aviões (5 casas)
- 1 encouraçado (4 casas)
- 1 cruzador (3 casas)
- 1 submarino (3 casas)
- 1 destróier (2 casas)

## Regras

- Cada tabuleiro possui uma grade de 10x10 casas, identificadas por letras (A-J) e números (1-10)
- Posicionamento dos navios:
  - Pode ser feito na vertical ou horizontal
  - Navios podem encostar entre si, mas não podem se sobrepor
- Um navio é considerado afundado quando todas as suas casas forem atingidas
- Um jogador não pode atacar a mesma coordenada mais de uma vez

## Turnos

- Os jogadores alternam turnos
- Em cada turno, o jogador escolhe uma coordenada para atacar (por exemplo, A5)
- O adversário deve responder com:
  - "Água" caso não haja navio na coordenada
  - "Atingido" caso haja um navio, mas ele ainda não tenha sido afundado
  - "Afundou" caso o ataque complete a destruição de um navio
- O jogador registra o resultado no seu tabuleiro de ataque

## Fim do jogo

O jogo termina quando um jogador afunda todos os navios do adversário. Esse jogador é declarado vencedor.

# Sobre a implementação

## Diretrizes

- Implementar em Python utilizando paradigma funcional
- Não utilizar classes
- Funções devem ser puras, sem efeitos colaterais e sem modificar o estado diretamente
- Funções que alteram o estado devem retornar uma nova versão do estado, sem modificar o original
- A lógica do jogo deve ser independente da interface
- A interface deve estar em um módulo separado e se comunicar com a lógica apenas por meio de funções puras

## Interface

- A interface gráfica deve ser implementada utilizando PyGame
- Deve representar o tabuleiro como uma grade de células
- Cada célula deve ter preenchimento suave e bordas mais destacadas
- Utilizar cores distintas para cada tipo de navio
- O design deve ser limpo e sem poluição visual

## Modos de jogo

- Deve ser possível jogar:
  - IA contra IA
  - Humano contra IA

## Inteligência artificial

- Utilizar o algoritmo Monte Carlo Tree Search (MCTS)
- Aplicar heurísticas para melhorar a eficiência da busca

## Testes

- Seguir a abordagem de TDD (Test-Driven Development)
- Começar sempre pelo caso mais simples possível
- Utilizar PyTest
- Testar apenas a interface pública do sistema

## Ferramentas e dependências

- Utilizar bibliotecas como NumPy e NetworkX quando necessário
- Gerenciar dependências com Poetry (pyproject.toml)
- Criar um Makefile para facilitar execução de testes, lint e outras tarefas
- Utilizar Black para formatação de código, seguindo PEP 8

## Convenções

- Comentários devem ser escritos em português
- Código deve ser escrito em inglês
- Comentários devem explicar decisões e algoritmos relevantes, evitando explicações óbvias e header comments, como: "Aqui estão as funções de utilidade para o jogo"

## Restrições

- Não utilizar classes
- Não incluir código morto
- Não comentar código autoexplicativo
- Não utilizar bibliotecas de IA pré-construídas como TensorFlow ou PyTorch

## Uso de IA generativa

- Utilizar IA generativa apenas para auxiliar na escrita de código, não para gerar código completo
