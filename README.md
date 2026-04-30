# batalha-naval

Este repositório contém a implementação do jogo de batalha naval em Python, com foco em conceitos de teoria dos jogos, inteligência artificial e algoritmos de busca competitiva.

Acesse em: https://lemuel-manske.github.io/batalha-naval/

# Ambiente

- Instalar `poetry`

```bash
poetry install
```

- Rodar testes

```bashbash
make test
```

Todos os comandos estão disponíveis em [Makefile](Makefile).

# Decisões

Decisões de algoritmos estão mantidas em [DECISIONS.md](DECISIONS.md).

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

- Lógica do jogo em Python, paradigma funcional (sem classes, funções puras, estado imutável)
- Interface web rodando inteiramente no browser via [Pyodide](https://pyodide.org) - o Python executa em um Web Worker, sem servidor
- Frontend em JS + CSS, sem frameworks
- IA usa estratégia *probability density + hunt/target*: modo alvo após um hit (foca nas adjacentes para afundar o navio) e modo caça com filtro de paridade e heatmap Monte Carlo no restante
- Dois modos de jogo: Humano vs IA e IA vs IA
- Testes com pytest; gerenciamento de dependências com Poetry
- Deploy automático no GitHub Pages via GitHub Actions
