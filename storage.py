"""Reads and writes transactions in finance_data.csv."""

import csv
import os
from datetime import datetime

import pandas as pd

CSV_FILE = "finance_data.csv"
COLUMNS = ["date", "amount", "category", "description"]

# Dates are stored as text like 31-12-2025 so the file is easy to read by hand.
DATE_FORMAT = "%d-%m-%Y"


def ensure_file_exists():
    """Creates finance_data.csv with just a header row if it doesn't exist yet."""
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, "w", newline="") as f:
            csv.writer(f).writerow(COLUMNS)


def add_transaction(date, amount, category, description):
    """Appends one transaction to the end of the file."""
    # If the file was last edited by hand and doesn't end with a line break,
    # add one first so the new row doesn't get glued onto the last row.
    with open(CSV_FILE, "rb") as f:
        contents = f.read()
    needs_newline = contents and not contents.endswith(b"\n")

    with open(CSV_FILE, "a", newline="") as f:
        if needs_newline:
            f.write("\n")
        csv.DictWriter(f, fieldnames=COLUMNS).writerow({
            "date": date,
            "amount": amount,
            "category": category,
            "description": description,
        })


def load_transactions(start_date, end_date):
    """Returns every transaction between two dates (inclusive), oldest first.

    `start_date` and `end_date` are strings like "01-01-2025".
    The returned table's "date" column holds real dates, ready for sorting and charting.
    """
    transactions = pd.read_csv(CSV_FILE)
    transactions["date"] = pd.to_datetime(transactions["date"], format=DATE_FORMAT)

    start = datetime.strptime(start_date, DATE_FORMAT)
    end = datetime.strptime(end_date, DATE_FORMAT)
    in_range = (transactions["date"] >= start) & (transactions["date"] <= end)

    return transactions[in_range].sort_values("date").reset_index(drop=True)
