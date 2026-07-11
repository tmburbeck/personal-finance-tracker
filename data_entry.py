"""
Input validation helpers for the finance tracker CLI.

Kept separate from main.py so that "how do we validate user input" is
isolated from "how do we store/query transactions" -- each function here
loops on itself (recursively re-prompting) until it gets valid input,
so callers never have to handle invalid input themselves.
"""

from datetime import datetime

CATEGORIES = {'I': 'Income', 'E': 'Expense'}


def get_date(prompt, allow_default=False):
    """
    Prompt for a date in dd-mm-yyyy format and return it as a string in
    that same format (kept as a string, not a datetime, since that's what
    gets written straight to the CSV).

    allow_default=True lets the user hit Enter on an empty prompt to use
    today's date -- handy for add() where most entries are for "today",
    but not used for the reporting date-range prompts where an accidental
    empty Enter shouldn't silently default to today.
    """
    date_str = input(prompt)
    if allow_default and not date_str:
        return datetime.today().strftime('%d-%m-%Y')
    try:
        valid_date = datetime.strptime(date_str, '%d-%m-%Y')
        return valid_date.strftime('%d-%m-%Y')
    except ValueError:
        print('Invalid date format. Please enter a valid date format: dd-mm-yyyy.')
        # Recursive re-prompt: keeps asking until it gets something valid.
        return get_date(prompt, allow_default)


def get_amount():
    """
    Prompt for a transaction amount and enforce that it's a positive
    number. float() raising ValueError on non-numeric input, and our own
    raise for negative amounts, both fall into the same except block, so
    either kind of bad input triggers the same re-prompt.
    """
    try:
        amount = float(input('Enter the amount: '))
        if amount <= 0:
            raise ValueError('Amount must be a non-negative, non-zero value.')
        return amount
    except ValueError as e:
        print(e)
        return get_amount()


def get_category():
    """
    Prompt for a category using single-letter shorthand (I/E) and map it
    to the full label ('Income'/'Expense') that gets stored in the CSV.
    .upper() makes the input case-insensitive.
    """
    category = input('Enter the category (I for "Income" or E for "Expense): ').upper()
    if category in CATEGORIES:
        return CATEGORIES[category]
    print('Invalid category. Please enter "I" for Income or "E" for Expense.')
    return get_category()


def get_description():
    """
    Free-text description -- no validation needed, so this is just a
    thin wrapper for consistency with the other get_* input functions.
    """
    return input('Enter the description: ')
