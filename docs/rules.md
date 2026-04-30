# Batalha Naval

## Descrição

Batalha Naval é um jogo de dois jogadores com informação imperfeita. Cada jogador posiciona seus navios secretamente em um tabuleiro 10×10 e, em turnos alternados, ataca coordenadas do tabuleiro adversário. O primeiro a afundar todos os navios do oponente vence.

## Regras

### Preparação

Cada jogador possui um tabuleiro 10×10 e os seguintes navios:

| Navio | Tamanho |
|---|---|
| Porta-aviões | 5 |
| Encouraçado | 4 |
| Cruzador | 3 |
| Submarino | 3 |
| Destroyer | 2 |

- Os navios podem ser posicionados na horizontal ou vertical
- Navios podem encostar entre si, mas não podem se sobrepor
- As posições são secretas — o adversário não vê o tabuleiro do oponente

### Turnos

- Os jogadores alternam turnos
- Em cada turno, o jogador escolhe uma coordenada `(linha, coluna)` do tabuleiro adversário que ainda não foi atacada
- O resultado do ataque é um de três valores:
  - **Água** — nenhum navio na coordenada
  - **Atingido** — há um navio, mas ele ainda não foi afundado
  - **Afundou** — o ataque completou a destruição de um navio

### Fim do jogo

O jogo termina quando todos os navios de um jogador forem afundados. O oponente é declarado vencedor.

---

## Formulação do Problema de Busca

O agente (IA) enfrenta um problema de busca com informação parcial: ele conhece apenas os resultados dos seus próprios ataques, não a posição real dos navios adversários.

### Estado

Um estado `s` é composto por:

- `ataques`: conjunto de coordenadas já atacadas e seus resultados (`água`, `atingido`, `afundou`)
- `navios_restantes`: dicionário de navios ainda não afundados do adversário, com as células que ainda estão de pé

```
s = (ataques, navios_restantes)
```

O estado captura tudo que o agente sabe sobre o tabuleiro adversário até o momento.

### Estado inicial

```
s₀ = (ataques = ∅, navios_restantes = {porta-aviões, encouraçado, cruzador, submarino, destroyer})
```

Nenhuma coordenada foi atacada; todos os 5 navios do adversário estão intactos (17 células ocupadas em posições desconhecidas).

### Estado objetivo

```
s* = (navios_restantes = ∅)
```

Todos os navios do adversário foram afundados — as 17 células de navios foram todas atingidas.

### Função sucessora (ações possíveis)

A partir de qualquer estado `s`, o conjunto de ações disponíveis é:

```
Ações(s) = { (r, c) | 0 ≤ r, c ≤ 9  e  (r, c) ∉ s.ataques }
```

Ou seja, qualquer coordenada do tabuleiro 10×10 ainda não atacada. Ao executar a ação `(r, c)`:

1. `(r, c)` é adicionado a `s.ataques` com o resultado correspondente
2. Se o ataque afundar um navio, ele é removido de `s.navios_restantes`
3. O estado resultante `s'` reflete o novo conhecimento acumulado

O número máximo de ações possíveis em `s₀` é 100 (tabuleiro vazio); o mínimo é 0 (estado objetivo atingido).

### Custo de caminho

O custo de um caminho é o número de ataques realizados até atingir o estado objetivo:

```
custo(s₀ → s₁ → ... → s*) = número de ataques
```

- **Custo mínimo teórico**: 17 — acertar diretamente todas as células de navios sem nenhum erro
- **Custo máximo teórico**: 100 — atacar todas as 100 células do tabuleiro

O objetivo da IA é minimizar esse custo, ou seja, afundar todos os navios no menor número de ataques possível. Como as posições são ocultas, o problema é de busca com informação parcial: o agente precisa inferir a distribuição de probabilidade das posições dos navios a partir dos resultados observados.

### Estratégia

A IA combina duas heurísticas:

- **Modo caça** (*hunting*): quando não há acertos ativos, filtra candidatos por paridade (descarta células onde o menor navio restante não cabe) e usa amostragem Monte Carlo para estimar a densidade de probabilidade de cada célula conter um navio
- **Modo alvo** (*targeting*): quando há acertos em navios ainda vivos, identifica sequências contíguas de acertos para determinar a orientação provável do navio e ataca as extremidades do segmento
