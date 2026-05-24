# Experiment & Analysis Scripts

Utility scripts for running experiments and analyzing results.

## Scripts

### `split_dataset.py`
Splits CSV datasets into multiple parts for multi-producer experiments.

**Usage:**
```bash
python scripts/split_dataset.py <num_parts> <input_file>
python scripts/split_dataset.py 2 datasets/lifestyle_progresspics.csv
```

### `visualize_results.py`
Generates visualization graphs from experiment metric reports.

**Usage:**
```bash
python scripts/visualize_results.py
```

Reads from `reports/` directory and generates `reports/experiment_results.png`.

### `run-all-experiments.sh`
Orchestrates a full suite of experiments with different configurations.

**Usage:**
```bash
bash scripts/run-all-experiments.sh
```

Runs experiments with various producer/partition/consumer configurations and generates reports.