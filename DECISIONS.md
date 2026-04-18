# Decisões de projeto

Este documento registra as decisões técnicas relevantes tomadas durante o desenvolvimento, com o racional por trás de cada escolha.

# Inteligência artificial

## Por que MCTS e não Minimax

Batalha naval é um jogo de **informação imperfeita**: cada jogador desconhece a posição dos navios do adversário. Essa característica inviabiliza o uso do Minimax clássico.

O Minimax pressupõe que ambos os jogadores enxergam o estado completo do jogo a cada turno. Em xadrez ou damas isso é verdade. Em batalha naval, o espaço de configurações possíveis dos navios inimigos é da ordem de 10^15, grande demais para ser explorado como árvore de decisão.

Além disso, a adversariedade do Minimax pressupõe que o oponente toma decisões ativas contra o jogador a cada turno. Em batalha naval, os navios já foram posicionados antes do jogo começar. Não há decisão adversarial contínua para o Minimax modelar.

O Monte Carlo Tree Search lida naturalmente com informação imperfeita:

- Amostra configurações plausíveis dos navios inimigos com base nos ataques já realizados
- Simula jogos completos a partir dessas configurações
- Agrega os resultados para estimar qual coordenada tem maior probabilidade de acerto

Em vez de explorar uma árvore exata, o MCTS aproxima a decisão ótima via amostragem e melhora quanto mais tempo tiver para executar.

## Extensibilidade para outros algoritmos

A interface de estratégia é definida como um callable puro:

```
Strategy = (GameState, Player) -> Coord
```

Qualquer algoritmo que respeite essa assinatura pode substituir o MCTS sem alterar o loop de jogo. Isso inclui variantes como Minimax com estados de crença (Belief-state Minimax), que mantém uma distribuição de probabilidade sobre os estados possíveis do tabuleiro inimigo em vez de operar sobre um estado único e observável.
