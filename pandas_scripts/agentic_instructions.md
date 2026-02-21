# agentic_instructions.md — python_projects/pandas_scripts

## Purpose
Pandas/Excel data processing scripts for Datadog integration management, with multiple implementation variants for reading, transforming, and writing integration lists to Excel.

## Technology
- Language: Python 3
- Libraries: pandas, xlsxwriter, openpyxl
- Data format: Excel (.xlsx)

## Contents
- `basic.py` — Pandas fundamentals: Series, DataFrame creation, Excel export with auto-column-width.
- `dd_integration.py` — Datadog integration list processing.
- `generalize.py` — Generalized data processing utility.
- `wallhaven_pandas.py` — Wallhaven API data processing with pandas.
- `testing_pandas.xlsx` / `fs_integrations_list.xlsx` — Sample Excel data files.
- `Makefile` — Build/run targets.
- `integrations/` — Datadog integration list management variant.
- `forest/` — Forest-specific Datadog integration scripts.
- `implementations/` — Implementation tracking with Excel I/O and README documentation.

## Key Functions
- `basic.py` — Creates Series/DataFrame, maps data, exports to Excel with formatted column widths.
- `dd_integration.py` — Reads integration lists, processes Datadog-specific data.
- `implementations/implementations.py` — Full implementation tracking workflow with Excel read/write.

## Data Types
- `pd.Series` — 1D labeled arrays.
- `pd.DataFrame` — 2D tabular data.
- Excel workbooks via `pd.ExcelWriter` with xlsxwriter engine.

## Logging
- `print()` for DataFrame output.

## CRUD Entry Points
- **Run**: `python3 basic.py` or `make` in subdirectories.
- **Dependencies**: `pip install pandas xlsxwriter openpyxl`

## Style Guide
- `pd.ExcelWriter` context manager for Excel output
- Column auto-width calculation pattern
- DataFrame operations chained with method syntax

```python
with pd.ExcelWriter('testing_pandas.xlsx', engine='xlsxwriter') as writer:
    df.to_excel(writer, sheet_name='turtles', index=False)
    worksheet = writer.sheets['turtles']
    for i, col in enumerate(df.columns):
        col_len = df[col].astype(str).apply(len)
        max_len = max(col_len.max(), len(col)) + 2
        worksheet.set_column(i, i, max_len)
```
