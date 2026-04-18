# Decisões de projeto

Este documento registra as decisões técnicas relevantes tomadas durante o desenvolvimento, com o racional por trás de cada escolha.

# Inteligência artificial

## Por que MCTS e não Minimax

Batalha naval é um jogo de **informação imperfeita**: cada jogador desconhece a posição dos navios do adversário. Essa característica inviabiliza o uso do Minimax clássico.

Russell & Norvig definem os jogos tratados pelo Minimax como "determinísticos, dois jogadores, revezamento, **informação perfeita**, jogos de soma zero" — onde "informação perfeita" é sinônimo de "totalmente observável" (cap. 5, seção 5.1.1). Batalha naval viola essa premissa: o tabuleiro inimigo nunca é observável.

O Minimax também pressupõe que o oponente toma decisões ativas a cada turno. Em batalha naval, os navios já foram posicionados antes do jogo começar — não há decisão adversarial contínua para o Minimax modelar.

Quanto à escala: Russell & Norvig mostram que a complexidade do Minimax é O(b^m), onde b é o fator de ramificação e m a profundidade (cap. 5, seção 5.2.1). Em batalha naval, o espaço de configurações possíveis dos navios inimigos é da ordem de 10^15 — intratável mesmo com poda alfabeta (seção 5.2.3).

A alternativa indicada pelo próprio livro para quando a busca precisa ser encerrada antes de atingir folhas é "calcular a média dos resultados de muitas simulações rápidas do jogo partindo desse estado até o fim" (seção 5.4) — que é exatamente o que o MCTS faz. O livro cita explicitamente jogos de informação imperfeita como pôquer e bridge como casos em que essa abordagem se aplica (seção 5.6).

O MCTS lida naturalmente com informação imperfeita:

- Amostra configurações plausíveis dos navios inimigos com base nos ataques já realizados
- Simula jogos completos a partir dessas configurações
- Agrega os resultados para estimar qual coordenada tem maior probabilidade de acerto

Em vez de explorar uma árvore exata, o MCTS aproxima a decisão ótima via amostragem e melhora quanto mais tempo tiver para executar.

## Budget de tempo em vez de número fixo de simulações

O MCTS é um **anytime algorithm**: pode ser interrompido a qualquer momento e retorna o melhor resultado parcial disponível.

Russell & Norvig descrevem o problema em cap. 5, seção 5.2: "para jogos não triviais, normalmente não teremos tempo suficiente para garantir que a jogada ótima foi encontrada; teremos que encerrar a busca em algum ponto." Para o Minimax, isso se resolve com iterative deepening — cada profundidade completa antes de avançar, garantindo sempre um resultado válido da última profundidade terminada.

No MCTS o mecanismo é mais simples: cada simulação já melhora incrementalmente as estimativas, sem dependência de profundidade. O critério de parada natural é, portanto, tempo — não número de simulações. Mais tempo resulta em mais simulações e estimativas estatisticamente mais precisas, o que se traduz diretamente em mais vitórias.

A função `mcts_strategy` aceita um parâmetro `time_budget` (padrão `MCTS_TIME_BUDGET = 0.4` segundos). Isso permite:

- Ajustar a dificuldade da IA mudando apenas o budget
- Adaptar ao hardware disponível sem alterar a lógica do algoritmo
- Usar budgets pequenos em testes para manter a suite rápida

## Por que substituir o MCTS por `smart_strategy`

O `mcts_strategy` tinha um defeito fundamental: usava `random_strategy` nas simulações internas. Isso tornava o algoritmo equivalente a um heatmap Monte Carlo puro — ele estimava a densidade de navios por célula, mas **ignorava completamente os hits já registrados**. Após acertar um navio, a IA continuava atirando aleatoriamente em vez de focar nas células adjacentes para afundá-lo.

A `smart_strategy` corrige isso com dois modos de operação:

**Modo alvo (target mode):** ativado quando há hits em navios ainda não afundados. A função identifica as células quentes (`_get_hot_cells`) e calcula os candidatos de ataque (`_target_candidates`): se os hits estão alinhados em uma linha ou coluna, retorna apenas os endpoints do segmento; se há um único hit isolado, retorna os quatro vizinhos. Esse modo garante que a IA afunde o navio antes de mudar de alvo.

**Modo caça (hunt mode):** ativado quando não há hits pendentes. Filtra as células candidatas pelo critério de paridade (`_parity_candidates`): só inclui células onde o menor navio ainda vivo cabe horizontalmente ou verticalmente sem passar por uma célula já atacada e errada. Isso reduz o espaço de busca em ~50% comparado ao tiro aleatório.

Em ambos os modos, quando há mais de um candidato, a decisão final usa amostragem Monte Carlo (`N_SAMPLES = 200` amostras via `sample_opponent_board`) para estimar a densidade de navios por célula, com tie-break por distância Manhattan ao centro do tabuleiro (4.5, 4.5).

O ganho prático do target mode é muito maior que o do heatmap: focar nos adjacentes após um hit é o que separa um jogador competente de um aleatório. O hunt mode com paridade reduz turnos desperdiçados em células onde nenhum navio pode estar.

## Extensibilidade para outros algoritmos

A interface de estratégia é definida como um callable puro:

```
Strategy = (GameState, Player) -> Coord
```

Qualquer algoritmo que respeite essa assinatura pode substituir o MCTS sem alterar o loop de jogo. Isso inclui variantes como Minimax com estados de crença (Belief-state Minimax), que mantém uma distribuição de probabilidade sobre os estados possíveis do tabuleiro inimigo em vez de operar sobre um estado único e observável — abordagem mencionada por Russell & Norvig na seção 5.6 para jogos de informação imperfeita.
