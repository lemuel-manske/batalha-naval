# Inteligência artificial

Qual algoritmo usar?

## Minimax

Minimas é, provavelmente, o algoritmo de busca mais conhecido para jogos de tabuleiro. Ele constrói uma árvore de jogo onde cada nó representa um estado do jogo e cada aresta representa uma jogada possível. O Minimax assume que o oponente joga de forma ótima, minimizando a chance de vitória do jogador.

Porém, o Minimax é inadequado para batalha naval por ser um **jogo de informação imperfeita**. O jogador não tem acesso ao estado completo do jogo (posição dos navios inimigos), o que inviabiliza a construção de uma árvore de jogo precisa.
Além disso, a complexidade combinatória do espaço de estados torna o Minimax impraticável mesmo com otimizações como poda alfabeta.

## Monte Carlo Tree Search (MCTS)

Comparado com o Minimax, o MCTS se torna a escolha natural para jogos de informação imperfeita como batalha naval. Ele é um algoritmo de busca baseado em amostragem que constrói uma árvore de jogo de forma incremental, explorando os nós mais promissores com base em simulações aleatórias.

O MCTS lida naturalmente com informação imperfeita:

- Amostra configurações plausíveis dos navios inimigos com base nos ataques já realizados
- Simula jogos completos a partir dessas configurações
- Agrega os resultados para estimar qual coordenada tem maior probabilidade de acerto

Em vez de explorar uma árvore exata, o MCTS aproxima a decisão ótima via amostragem e melhora quanto mais tempo tiver para executar.

### Budget de tempo em vez de número fixo de simulações

O MCTS é um **anytime algorithm**: pode ser interrompido a qualquer momento e retorna o melhor resultado parcial disponível.

Poderíamos, por exemplo, rodar infinitas simulações e parar quando o tempo esgotar. Mas, obviamente, o jogo tem que acabar em algum momento, então precisamos de um critério de parada.

Foi introduzido um budget de tempo (em segundos) para controlar a execução do MCTS. Isso tem várias vantagens:

- Ajustar a dificuldade da IA mudando apenas o budget
- Adaptar ao hardware disponível sem alterar a lógica do algoritmo
- Usar budgets pequenos em testes para manter a suite rápida

## Combinação de MCTS com heurísticas de caça e alvo

O que torna o MTCS limitado? As simulações internas usam uma estratégia aleatória para escolher os ataques, o que é ineficiente. O MCTS pode ser muito lento para convergir se as simulações não forem informadas por heurísticas de jogo.

Por exemplo, o MTCS **ignorava completamente os hits já registrados**. Após acertar um navio, a IA continuava atirando aleatoriamente em vez de focar nas células adjacentes para afundá-lo.

A nova estratégia corrige isso com dois modos de operação:

**Modo alvo (target):** ativado quando há hits em navios ainda não afundados. A função identifica as células "quentes" e calcula os candidatos de ataque: se os hits estão alinhados em uma linha ou coluna, retorna apenas os endpoints do segmento; se há um único hit isolado, retorna os quatro vizinhos. Esse modo garante que a IA afunde o navio antes de mudar de alvo.

**Modo caça (hunt):** ativado quando não há hits pendentes. Filtra as células candidatas pelo critério de paridade: só inclui células onde o menor navio ainda vivo cabe horizontalmente ou verticalmente sem passar por uma célula já atacada e errada. Isso reduz o espaço de busca em ~50% comparado ao tiro aleatório.

Em ambos os modos, quando há mais de um candidato, a decisão final usa amostragem Monte Carlo para estimar a densidade de navios por célula, com tie-break por distância Manhattan ao centro do tabuleiro.

O ganho prático do target mode é muito maior que o do heatmap: focar nos adjacentes após um hit é o que separa um jogador competente de um aleatório. O hunt mode com paridade reduz turnos desperdiçados em células onde nenhum navio pode estar.

# Conclusão

A combinação de MCTS com heurísticas de caça e alvo é uma solução elegante para a IA de batalha naval.

O MCTS lida com a incerteza do jogo, enquanto as heurísticas guiam a busca para áreas mais promissoras do tabuleiro. O resultado é uma IA que oferece um desafio interessante para os jogadores humanos.
