"""
Personal Finance Tracker
-------------------------
A command-line application for logging income/expenses to a CSV file,
filtering transactions by date range, and visualizing income vs. expenses
over time with matplotlib.

Architecture:
- CSV class: handles all file I/O (create, append, read/filter) and acts
  as a lightweight data-access layer so the rest of the app never touches
  the raw file directly.
- data_entry module: handles user input validation (dates, amounts,
  categories, descriptions) and is kept separate so input-parsing logic
  doesn't clutter the data layer or the main loop.
- main(): a simple CLI menu that ties everything together.
"""

import pandas as pd
import csv
from datetime import datetime

from matplotlib import pyplot as plt

from data_entry import get_amount, get_date, get_category, get_description


class CSV:
    """
    Wraps all CSV read/write logic for transactions in one place.
    Using classmethods (rather than instantiating CSV objects) keeps this
    as a simple namespaced utility, since there's no per-instance state --
    every transaction goes to the same file.
    """

    CSV_FILE = 'finance_data.csv'
    COLUMNS = ['date', 'amount', 'category', 'description']
    # Storing dates as dd-mm-yyyy strings in the CSV keeps the raw file
    # human-readable; we only convert to datetime objects in memory when
    # we need to filter or plot.
    FORMAT = '%d-%m-%Y'

    @classmethod
    def initialize_csv(cls):
        """
        Ensure finance_data.csv exists with the correct header row before
        anything tries to read from or append to it. If the file is
        missing, pandas raises FileNotFoundError, which we catch and use
        as the trigger to create an empty file with just the headers.
        """
        try:
            pd.read_csv(cls.CSV_FILE)
        except FileNotFoundError:
            df = pd.DataFrame(columns=cls.COLUMNS)
            df.to_csv(cls.CSV_FILE, index=False)

    @classmethod
    def add_entry(cls, date, amount, category, description):
        """
        Append a single transaction as a new row. Using csv.DictWriter in
        'a' (append) mode is more efficient than reading the whole file
        into a DataFrame just to add one row -- we only pay the pandas
        read/write cost when we actually need to filter or summarize.
        """
        new_entry = {
            'date': date,
            'amount': amount,
            'category': category,
            'description': description
        }
        with open(cls.CSV_FILE, 'a', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=cls.COLUMNS)
            writer.writerow(new_entry)
        print('Entry added successfully')

    @classmethod
    def get_transactions(cls, start_date, end_date):
        """
        Load all transactions, filter them to the given date range, print
        a formatted table plus an income/expense/net-savings summary, and
        return the filtered DataFrame so callers (like plot_transactions)
        can reuse it without re-reading the file.
        """
        df = pd.read_csv(cls.CSV_FILE)
        # Convert the 'date' column from strings to real datetime objects
        # so we can do range comparisons (>=, <=) below.
        df['date'] = pd.to_datetime(df['date'], format=CSV.FORMAT)
        start_date = datetime.strptime(start_date, CSV.FORMAT)
        end_date = datetime.strptime(end_date, CSV.FORMAT)

        # Boolean mask selects only rows within the requested date range.
        mask = (df['date'] >= start_date) & (df['date'] <= end_date)
        filtered_df = df.loc[mask]

        if filtered_df.empty:
            print('No transactions found in date range.')
        else:
            print(
                f'Transactions from {start_date.strftime(CSV.FORMAT)} to {end_date.strftime(CSV.FORMAT)}:'
            )
            print(
                filtered_df.to_string(
                    index=False, formatters={'date': lambda x: x.strftime(CSV.FORMAT)})
            )

            # Sum amounts separately by category to build the summary.
            total_income = filtered_df[filtered_df['category'] == 'Income']['amount'].sum()
            total_expense = filtered_df[filtered_df['category'] == 'Expense']['amount'].sum()
            print('\nSummary:')
            print(f'\nTotal income: ${total_income:.2f}')
            print(f'\nTotal expense: ${total_expense:.2f}')
            print(f'\nNet savings: ${total_income - total_expense:.2f}')

        # Returned (not just printed) so plot_transactions() and any
        # future callers can reuse the same filtered data.
        return filtered_df


def add():
    """
    CLI flow for adding a single transaction: makes sure the CSV exists,
    collects validated input for each field, then writes the row.
    """
    CSV.initialize_csv()
    date = get_date(
        'Enter the date of the transaction (dd-mm-yyyy) or enter for today\'s date: ',
        allow_default=True,
    )
    amount = get_amount()
    category = get_category()
    description = get_description()
    CSV.add_entry(date, amount, category, description)


def plot_transactions(df):
    """
    Plot income and expenses over time as two line series.

    resample('D') buckets transactions by calendar day and sums same-day
    amounts together, which is what makes multiple transactions on one
    day collapse into a single point on the line. reindex(df.index, ...)
    then fills in any days with no transactions as 0 (instead of leaving
    a gap), so both lines span the full date range continuously.

    Note: we select ['amount'] before resampling/summing so we're only
    aggregating the numeric column -- summing the 'category' and
    'description' string columns would error out.
    """
    df.set_index('date', inplace=True)
    income_df = df[df['category'] == 'Income']['amount'].resample('D').sum().reindex(df.index, fill_value=0)
    expense_df = df[df['category'] == 'Expense']['amount'].resample('D').sum().reindex(df.index, fill_value=0)

    plt.figure(figsize=(12, 8))
    plt.plot(income_df.index, income_df, label='Income', color='blue')
    plt.plot(expense_df.index, expense_df, label='Expense', color='red')
    plt.xlabel('Date')
    plt.ylabel('Amount')
    plt.title('Income and Expenses over time')
    plt.legend()
    plt.grid(True)
    plt.show()


def main():
    """
    Simple text-menu CLI loop. Kept intentionally minimal (no argparse,
    no subcommands) since the whole point is fast, low-friction manual
    entry -- this is meant to be run interactively, not scripted.
    """
    while True:
        print('\n1. Add a new transaction')
        print('2. View transactions and summary')
        print('3. Exit')
        choice = input('Enter your choice: (1-3):')
        if choice == '1':
            add()
        elif choice == '2':
            start_date = get_date('Enter the start date (dd-mm-yyyy): ')
            end_date = get_date('Enter the end date (dd-mm-yyyy): ')
            df = CSV.get_transactions(start_date, end_date)
            if input('Do you want to see a plot? (y/n): ').lower() == 'y':
                plot_transactions(df)
        elif choice == '3':
            print('Exiting...')
            break
        else:
            print('Invalid choice. Please enter 1, 2, or 3.')


if __name__ == '__main__':
    main()
