# batalha-naval

Battleship game in Python with a browser-based frontend.

Game logic runs entirely in the browser via [Pyodide](https://pyodide.org).

Live at: https://lemuel-manske.github.io/batalha-naval/

## Setup

Requires [Poetry](https://python-poetry.org).

```sh
poetry install
```

## Commands

| Command | Description |
|---|---|
| `make test-py` | Run Python tests |
| `make test-js` | Run JS tests |
| `make test` | Run both |
| `make fmt` | Format code with Black |
| `make lint` | Check formatting |
| `make typecheck` | Run mypy |
| `make build-web` | Sync Python package into `web/` |
| `make serve` | Serve the frontend at `localhost:8000` |

## Architecture

Game logic is implemented in Python, functional style, immutable state.

The web frontend loads the Python package into a Web Worker via Pyodide and communicates through a message protocol.

See [`web/`](web/) for frontend details.

## AI strategy

The AI uses a *probability density + hunt/target* approach:

- **Hunt mode** — parity filter and Monte Carlo heatmap to pick the highest-probability cell
- **Target mode** — after a hit, focuses on adjacent cells to finish sinking the ship

## Docs

- [Game rules](./docs/rules.md)
- [Algorithm decisions](./docs/decisions.md)
