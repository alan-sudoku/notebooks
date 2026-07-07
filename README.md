# Notebooks

Interactive notebooks for the [alan-sudoku](https://alan-sudoku.github.io) research documents. Built with [marimo](https://marimo.io) — reactive Python notebooks runnable locally or on Marimo Cloud.

## Setup

```bash
pip install marimo matplotlib numpy
```

## Notebooks

### GSH — Geometric Sufficiency Hypothesis

| Notebook | Description |
|---|---|
| [fe_crossover_numeric.py](GSH/fe_crossover_numeric.py) | Fe/Al τ* crossover — numeric instance of OQ-GSH.8. Computes the deployment lifetime at which an Al geometric substitute becomes entropically cheaper than the Fe incumbent. Interactive sliders for mass, surface area, and corrosion rate. |

## Running locally

```bash
marimo edit GSH/fe_crossover_numeric.py
```

## Source documents

- [Geometric Sufficiency Hypothesis](https://alan-sudoku.github.io/gsh/geometric_sufficiency_hypothesis) — primary document
- [GSH Mathematical Inventory](https://alan-sudoku.github.io/gsh/gsh_mathematical_inventory) — formula reference
