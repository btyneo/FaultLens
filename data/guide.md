## Overview

Download the MetroPT-3 CSV file from the [UCI Machine Learning Repository](https://archive.ics.uci.edu/dataset/791/metropt+3+dataset), extract it, and save it in `data/raw/`.

`ingest.py` locates its own folder regardless of the current working directory, then finds all `.csv` files in `data/raw/`, concatenates them, and preprocesses the result. It returns a cleaned DataFrame with a sorted timestamp index.

*(For the current state of the project / v1, there's only one `.csv` file.)*

## Usage

Run directly:

```bash
python data/ingest.py
```

Or import the function:

```python
from data.ingest import get_dataframe
```