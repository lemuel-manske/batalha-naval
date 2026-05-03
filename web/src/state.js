export const uiState = {
  phase: "loading",
  mode: "hvai",
  strategy: {
    hvai:     "smart",
    p1_aivai: "smart",
    p2_aivai: "smart",
  },
  players: {
    player1: {
      pendingShips: [],
      placedShips: [],
      placementBoard: null,
      currentDir: "h",
    },
    player2: {
      pendingShips: [],
      placedShips: [],
      placementBoard: null,
      currentDir: "h",
    },
  },
  drag: { ship: null, cell: null },
  aiScheduled: false,
  gameState: null,
}
