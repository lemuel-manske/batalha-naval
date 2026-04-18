export const BOARD_SIZE = 10;
export const AI_TURN_DELAY_MS = 300;
export const AIVAI_TURN_DELAY_MS = 600;

export const SHIP_LABELS = {
  carrier: "Porta-aviões (5)",
  battleship: "Encouraçado (4)",
  cruiser: "Cruzador (3)",
  submarine: "Submarino (3)",
  destroyer: "Destroyer (2)",
};

export const MODE_CONFIG = {
  hvai: {
    labelPlayer: "Seu tabuleiro",
    labelEnemy: "Tabuleiro inimigo",
    statusPlacement: "Posicione seus navios e clique em Iniciar jogo.",
    statusTurnPlayer1: "Sua vez — clique no tabuleiro inimigo",
    statusTurnPlayer2: "IA pensando...",
    winPlayer1: "Você venceu!",
    winPlayer2: "IA venceu!",
  },
  aivai: {
    labelPlayer: "IA 1",
    labelEnemy: "IA 2",
    statusPlacement: "Posicione os navios de ambas as IAs e clique em Iniciar jogo.",
    statusTurnPlayer1: "Turno: IA 1",
    statusTurnPlayer2: "Turno: IA 2",
    winPlayer1: "IA 1 venceu!",
    winPlayer2: "IA 2 venceu!",
  },
};
