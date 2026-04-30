# batalha-naval - web

Browser frontend for the Battleship game. The Python game engine runs entirely in the browser via [Pyodide](https://pyodide.org) inside a Web Worker — no server required after the initial load.

## Setup

Requires [nvm](https://github.com/nvm-sh/nvm).

```sh
nvm install
nvm use

npm ci
```

## Commands

| Command | Description |
|---|---|
| `npm test` | Run the test suite once |
