# Kinetix Experiment Results & Visualization

## Overview

This directory contains evaluation results and plotting scripts for comparing **Real-Time Control (RTC)** methods on the **Kinetix** environment suite. The experiments compare two model families — a **continuous flow-matching** basemodel and a **discrete diffusion** model — across 12 Kinetix levels under varying inference delays.

---

## Data

All data is under `data/`, organized by model/method variant:

### `data/flow/results.csv` — Continuous Flow-Matching Basemodel

- **Columns:** `returned_episode_lengths`, `returned_episode_returns`, `returned_episode_solved`, `delay`, `method`, `level`, `execute_horizon`
- **Methods:** `naive`, `realtime` (continuous RTC), `bid`, `hard_masking`
- **Description:** Results from evaluating the continuous flow-matching model. The method `realtime` is the continuous RTC approach; `naive` is synchronous (wait-then-act); `bid` is the BID baseline; `hard_masking` is a masking-based baseline.

### `data/dd/results.csv` — Discrete Diffusion Model

- **Columns:** `delay`, `method`, `level`, `execute_horizon`, `mean_inference_s`, `mean_task_completion_time_s`, `returned_episode_lengths`, `returned_episode_returns`, `returned_episode_solved`, `worker_id`
- **Methods:** `naive`, `discrete_rtc`, `bid`, `adaptive_discrete_rtc`
- **Description:** Results from the discrete diffusion model. `discrete_rtc` is the discrete RTC method; `adaptive_discrete_rtc` is an adaptive variant. Includes per-worker timing data (`mean_inference_s`, `mean_task_completion_time_s`, `worker_id`). Combined from multiple worker CSV files.

### `data/dd-vlash/results.csv` — Discrete Diffusion with VLASH

- **Columns:** `delay`, `method`, `level`, `execute_horizon`, `mean_inference_s`, `mean_task_completion_time_s`, `returned_episode_lengths`, `returned_episode_returns`, `returned_episode_solved`
- **Methods:** `vlash`
- **Description:** Results for the VLASH (variable-length action sequence with heuristic) method, evaluated on the same discrete diffusion model and same 12 levels. Includes inference timing.

### `data/training_time/results.csv` — Training-Time Variant (Continuous)

- **Columns:** `returned_episode_lengths`, `returned_episode_returns`, `returned_episode_solved`, `delay`, `method`, `level`, `execute_horizon`
- **Methods:** `naive`, `realtime`, `bid`, `hard_masking`
- **Description:** A variant of the continuous flow-matching evaluation, possibly at a different training checkpoint or with different training-time configurations.

### Evaluation Configs

- `data/dd/eval_config.json` — Config for the discrete diffusion evaluation. Defines sweep over `inference_delays` [0–4], `execute_horizon = max(1, delay)`, and methods `naive`, `discrete_rtc`, `bid`. Model uses 512 bins, 8-step action chunks, 4 transformer layers, and cosine decode schedule. Run path: `./logs-dd/l1`.
- `data/dd-vlash/eval_config.json` — Config for the VLASH evaluation. Same sweep structure and model architecture, but methods include `vlash` in addition to `naive`, `discrete_rtc`, `bid`. Run path: `./logs-dd/l1_vlash`.

### Common Fields

| Field | Description |
|---|---|
| `delay` | Inference delay `d` (0, 1, 2, 3, 4) — how many timesteps the policy lags behind the environment |
| `execute_horizon` | Number of actions executed per inference call `s`, set to `max(1, d)` |
| `method` | Baseline/algorithm name |
| `level` | Kinetix level path (e.g., `worlds/l/grasp_easy.json`) |
| `returned_episode_solved` | Fraction of episodes solved (primary metric) |
| `returned_episode_returns` | Mean episode return |
| `returned_episode_lengths` | Mean episode length in timesteps |
| `mean_inference_s` | Mean wall-clock inference time per action (seconds), available in `dd` and `dd-vlash` |

### 12 Kinetix Levels

`grasp_easy`, `catapult`, `cartpole_thrust`, `hard_lunar_lander`, `mjc_half_cheetah`, `mjc_swimmer`, `mjc_walker`, `h17_unicycle`, `chain_lander`, `catcher_v3`, `trampoline`, `car_launch`

---

## Plotting Scripts

### `plot_results.py` — Single-Dataset Visualization Suite

A comprehensive library of plotting functions for analyzing a **single** results CSV. Can be run as a CLI tool or imported as a module.

**CLI usage:**
```bash
python plot_results.py --csv data/dd/results.csv --output-dir main/ --no-show
python plot_results.py --csv data/flow/results.csv --output-dir main/ --method realtime
```

**Key functions:**

| Function | Plot Type | Description |
|---|---|---|
| `plot_solve_rate_by_delay_horizon()` | Heatmap | Solve rate vs (delay, execute_horizon) for one method |
| `plot_method_comparison()` | Bar chart | Compare all methods' mean metric, aggregated or per-level |
| `plot_delay_effect()` | Line plot | Metric vs delay, one line per execute_horizon |
| `plot_delay_vs_success_by_method()` | Line plot | Success vs delay with `s = max(1, d)`, one line per method. Includes a top x-axis for realtime delay=0 reference |
| `plot_per_level_heatmap()` | Heatmap | Per-level metric breakdown by (delay, execute_horizon) |
| `plot_mean_inference_time()` | Bar + Line | Mean inference time by method and vs delay |
| `plot_total_eval_wall_time()` | Grouped bar | Total evaluation wall time per (delay, method) |
| `plot_episode_length_by_delay_horizon()` | Heatmap | Episode length vs (delay, execute_horizon) |
| `plot_episode_length_delay_effect()` | Line plot | Episode length vs delay per execute_horizon |
| `plot_episode_length_vs_delay_by_method()` | Line plot | Episode length vs delay with `s = max(1, d)`, per method |
| `plot_episode_length_per_level_heatmap()` | Heatmap | Per-level episode length breakdown |
| `plot_method_comparison_episode_length()` | Bar chart | Compare methods by episode length |
| `plot_all()` | All above | Orchestrator that generates every plot for a given CSV |

**Features:**
- Normalizes episode length by each level's `max_timesteps` (loaded from level JSON files via `--project-root`)
- Computes reciprocal of normalized episode length (higher = faster task completion)
- CLI args: `--csv`, `--output-dir`, `--method`, `--no-show`, `--project-root`

---

### `plot_comparison_grid.py` — Cross-Model Solve Rate Comparison Grid

Generates a publication-quality **4x4 grid figure** comparing continuous vs discrete models side-by-side on **solve rate**.

**CLI usage:**
```bash
python plot_comparison_grid.py \
  --continuous-csv data/flow/results.csv \
  --discrete-csv data/dd/results.csv \
  --output main/comparison_grid.png \
  --no-show
```

**Layout:**
- **Rows 0–1 (2x4):** 8 individual environment subplots
- **Rows 2–3, Cols 0–1 (2x2):** "Average Over Environments" summary plot with legend
- **Rows 2–3, Cols 2–3 (2x2):** 4 remaining environment subplots

**Method naming convention:**
- Continuous methods are prefixed `continuous` (e.g., `continuousRTC`, `continuousnaive`, `continuousbid`)
- Discrete methods are prefixed `discrete` (e.g., `discreteRTC`, `discretenaive`, `discretebid`)
- `realtime` is renamed to `RTC`; `discrete_rtc` is renamed to `RTC`

**Color scheme:**
- Green (`#2ca02c`) for continuous family
- Red (`#d62728`) for discrete family
- Alpha/gray-blending distinguishes variants: RTC (full), BID (0.7), Naive (0.4)

**Key features:**
- Filters data to `execute_horizon = max(1, delay)` for consistent comparison
- `--show-sync` flag adds synthetic "Sync" baselines (delay=0 performance projected across delays)
- Utility function `combine_l1_complete()` merges per-worker CSVs into a single file
- Saves a standalone "Average Over Environments" figure alongside the grid (`*_average.png`)

---

### `plot_comparison_grid_episode_length.py` — Cross-Model Episode Length Comparison Grid

Same grid layout as `plot_comparison_grid.py`, but plots **normalized throughput** (reciprocal of normalized episode length) instead of solve rate.

**CLI usage:**
```bash
python plot_comparison_grid_episode_length.py \
  --continuous-csv data/flow/results.csv \
  --discrete-csv data/dd/results.csv \
  --output throughoutput/comparison_grid_episode_length.png \
  --project-root /path/to/kinetix/project \
  --no-show
```

**Differences from `plot_comparison_grid.py`:**
- Metric: `episode_length_reciprocal` (= 1 / (episode_length / max_timesteps))
- Y-axis label: "Normalized Throughputs"
- Requires `--project-root` to resolve level JSON files for `max_timesteps` normalization
- Y-axis range for average plot: [3.1, 4.4] (tuned for this metric)

---

## Output Directories

| Directory | Purpose |
|---|---|
| `main/` | Output for single-dataset plots and the solve-rate comparison grid |
| `flex/` | (Empty) Reserved for flexible/alternative visualizations |
| `throughoutput/` | Output for episode-length/throughput comparison grid figures |
