"""Asks the user for each piece of a transaction, re-asking until the answer is valid."""

from datetime import datetime

from storage import DATE_FORMAT

# The user types a single letter; the full word is what gets saved.
CATEGORIES = {"I": "Income", "E": "Expense"}


def get_date(prompt, allow_default=False):
    """Asks for a date in dd-mm-yyyy format and returns it as text in that format.

    With `allow_default=True`, pressing Enter on an empty prompt means "today".
    """
    while True:
        answer = input(prompt).strip()

        if allow_default and not answer:
            return datetime.today().strftime(DATE_FORMAT)

        try:
            return datetime.strptime(answer, DATE_FORMAT).strftime(DATE_FORMAT)
        except ValueError:
            print("Invalid date. Please use the format dd-mm-yyyy, e.g. 31-12-2025.")


def get_amount():
    """Asks for a positive amount of money and returns it as a number."""
    while True:
        answer = input("Enter the amount: ").strip()

        try:
            amount = float(answer)
        except ValueError:
            print("Please enter a number, e.g. 42.50.")
            continue

        if amount > 0:
            return amount
        print("The amount must be greater than zero.")


def get_category():
    """Asks whether this is income (I) or an expense (E) and returns "Income" or "Expense"."""
    while True:
        answer = input('Enter the category ("I" for Income or "E" for Expense): ').strip().upper()
        if answer in CATEGORIES:
            return CATEGORIES[answer]
        print('Please enter "I" for Income or "E" for Expense.')


def get_description():
    """Asks for a short free-text description, e.g. "groceries"."""
    return input("Enter the description: ").strip()
