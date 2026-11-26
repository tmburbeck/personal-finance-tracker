"""Personal Finance Tracker: a command-line app for logging income and expenses.

Files:
  main.py        the menu (this file)
  data_entry.py  asks the user for each field and checks the answer
  storage.py     reads and writes finance_data.csv
  charts.py      draws the dashboard
"""

from charts import show_dashboard, totals
from data_entry import get_amount, get_category, get_date, get_description
from storage import DATE_FORMAT, add_transaction, ensure_file_exists, load_transactions

MENU = """
1. Add a new transaction
2. View transactions and summary
3. Exit"""


def add():
    """Walks the user through entering one transaction, then saves it."""
    date = get_date("Enter the date of the transaction (dd-mm-yyyy), or press Enter for today: ",
                    allow_default=True)
    amount = get_amount()
    category = get_category()
    description = get_description()

    add_transaction(date, amount, category, description)
    print("Transaction added.")


def view():
    """Shows the transactions in a date range, a summary, and (optionally) the dashboard."""
    start_date = get_date("Enter the start date (dd-mm-yyyy): ")
    end_date = get_date("Enter the end date (dd-mm-yyyy): ")

    transactions = load_transactions(start_date, end_date)
    if transactions.empty:
        print("No transactions found in that date range.")
        return

    print(f"\nTransactions from {start_date} to {end_date}:\n")
    print(transactions.to_string(index=False, formatters={"date": lambda d: d.strftime(DATE_FORMAT)}))

    income, expenses = totals(transactions)
    print("\nSummary:")
    print(f"  Total income:   ${income:,.2f}")
    print(f"  Total expenses: ${expenses:,.2f}")
    print(f"  Net savings:    ${income - expenses:,.2f}")

    if input("\nOpen the dashboard chart? (y/n): ").strip().lower() == "y":
        show_dashboard(transactions)


def main():
    ensure_file_exists()

    while True:
        print(MENU)
        choice = input("Enter your choice (1-3): ").strip()

        if choice == "1":
            add()
        elif choice == "2":
            view()
        elif choice == "3":
            print("Goodbye!")
            break
        else:
            print("Please enter 1, 2, or 3.")


if __name__ == "__main__":
    main()
