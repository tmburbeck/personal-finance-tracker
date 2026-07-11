# Personal Finance Tracker

A command-line personal finance tracker built in Python. Log income and expenses to a CSV file, filter and summarize transactions by date range, and visualize income vs. expenses over time with matplotlib.

## Features

- **Add transactions** — record date, amount, category (Income/Expense), and description
- **Input validation** — dates, amounts, and categories are validated on entry, with automatic re-prompting on bad input
- **Date-range filtering** — view all transactions between a start and end date
- **Automatic summary** — total income, total expenses, and net savings for the selected range
- **Visualization** — plot daily income and expenses as line charts over the selected date range
- **CSV-backed storage** — human-readable, portable data file with no external database required

## Tech Stack

- Python 3
- [pandas](https://pandas.pydata.org/) — data filtering, aggregation, and date handling
- [matplotlib](https://matplotlib.org/) — plotting
- Python's built-in `csv` and `datetime` modules

## Project Structure

```
.
├── main.py          # CLI entry point, CSV data access layer, plotting
├── data_entry.py     # Input validation/prompting helpers
├── finance_data.csv  # Generated on first run — stores transactions
└── README.md
```

## How It Works

- `CSV` (in `main.py`) is a small classmethod-based utility that owns all reads/writes to `finance_data.csv`. It initializes the file with headers if missing, appends new transactions with `csv.DictWriter`, and uses pandas to filter by date range and compute summaries.
- `data_entry.py` handles all user input validation independently of the data layer, so each `get_*` function loops on itself until it receives valid input.
- `plot_transactions()` resamples the filtered transactions to daily totals (filling days with no activity as 0) and plots income vs. expenses as two line series.

## Getting Started

### Prerequisites

- Python 3.9+
- pip

### Installation

```bash
git clone https://github.com/tmburbeck/personal-finance-tracker.git
cd personal-finance-tracker
pip install pandas matplotlib
```

### Usage

```bash
python main.py
```

You'll see a simple menu:

```
1. Add a new transaction
2. View transactions and summary
3. Exit
```

- **Option 1** walks you through entering a date, amount, category, and description.
- **Option 2** asks for a start and end date, prints a formatted transaction table and summary, and offers to show a plot.
- **Option 3** exits the program.

Dates are entered in `dd-mm-yyyy` format.

## Possible Next Steps

- Move storage from CSV to SQLite/PostgreSQL for more robust querying
- Add a budget-vs-actual view by category
- Add monthly/yearly aggregate views alongside the daily plot
- Build a simple web UI (Flask) on top of the same `CSV`/data layer
- Export summary reports to PDF

## License

MIT
