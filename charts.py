"""Draws a one-page dashboard of the selected transactions.

The dashboard has four parts:
  1. Headline totals:   income, expenses and net savings for the period
  2. Month by month:    income and expenses side by side for each month
  3. Running balance:   how total savings have built up (or drained) over time
  4. Biggest expenses:  where the money went, grouped by description
"""

import math
import os
import subprocess
import sys

import matplotlib

matplotlib.use("Agg")  # draw straight to an image file; no on-screen window needed

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.ticker import FuncFormatter

# ---- Colors -----------------------------------------------------------------
# Income is always blue and expenses always orange, in every chart.
# This pair stays distinguishable for colorblind readers.
INCOME_COLOR = "#257de0"
EXPENSE_COLOR = "#f47230"

# Text and background colors (text is never drawn in a data color).
TEXT_PRIMARY = "#191919"
TEXT_SECONDARY = "#666666"
GRID_COLOR = "#e6e6e6"
BACKGROUND = "#ffffff"

# How many expense descriptions to show before grouping the rest as "Other".
TOP_EXPENSES = 7


DASHBOARD_FILE = "dashboard.png"


def show_dashboard(transactions):
    """Saves the dashboard as dashboard.png and opens it in the computer's image viewer."""
    path = os.path.abspath(DASHBOARD_FILE)
    save_dashboard(transactions, path)
    print(f"Dashboard saved to {path}")

    try:
        open_file(path)
        print("Opening it in your image viewer...")
    except OSError:
        print("Open that file to see the dashboard.")


def open_file(path):
    """Opens a file with whatever program the computer normally uses for it."""
    if sys.platform == "win32":
        os.startfile(path)  # Windows
    elif sys.platform == "darwin":
        subprocess.run(["open", path], check=True)  # macOS
    else:
        subprocess.run(["xdg-open", path], check=True)  # Linux


def save_dashboard(transactions, path):
    """Draws the dashboard and saves it as an image at `path`."""
    fig = plt.figure(figsize=(13, 9), facecolor=BACKGROUND)
    layout = fig.add_gridspec(3, 2, height_ratios=[0.5, 1.2, 1.2], hspace=0.6, wspace=0.4)

    start = transactions["date"].min().strftime("%b %d, %Y")
    end = transactions["date"].max().strftime("%b %d, %Y")
    fig.suptitle(f"Your finances, {start} to {end}", x=0.06, ha="left",
                 fontsize=16, fontweight="bold", color=TEXT_PRIMARY)

    draw_headline_totals(fig, layout[0, :], transactions)
    draw_monthly_columns(fig.add_subplot(layout[1, :]), transactions)
    draw_running_balance(fig.add_subplot(layout[2, 0]), transactions)
    draw_top_expenses(fig.add_subplot(layout[2, 1]), transactions)

    fig.savefig(path, dpi=150, bbox_inches="tight", facecolor=BACKGROUND)
    plt.close(fig)


# ---- The four parts -----------------------------------------------------------


def draw_headline_totals(fig, area, transactions):
    """Three big numbers across the top: income, expenses and net savings."""
    income, expenses = totals(transactions)
    net = income - expenses

    tiles = [
        ("Total income", money(income)),
        ("Total expenses", money(expenses)),
        ("Net savings", money(net, signed=True)),
    ]

    tile_areas = area.subgridspec(1, 3)
    for position, (label, value) in enumerate(tiles):
        ax = fig.add_subplot(tile_areas[0, position])
        ax.axis("off")
        ax.text(0, 0.75, label, fontsize=11, color=TEXT_SECONDARY, transform=ax.transAxes)
        ax.text(0, 0.05, value, fontsize=26, fontweight="bold", color=TEXT_PRIMARY,
                transform=ax.transAxes)


def draw_monthly_columns(ax, transactions):
    """Income and expense columns side by side for every month, including empty months."""
    by_month = (
        transactions
        .assign(month=transactions["date"].dt.to_period("M"))
        .pivot_table(index="month", columns="category", values="amount", aggfunc="sum")
    )
    # Show every month in the range, even ones with no transactions.
    all_months = pd.period_range(by_month.index.min(), by_month.index.max(), freq="M")
    by_month = by_month.reindex(all_months, fill_value=0).fillna(0)

    income = by_month.get("Income", pd.Series(0, index=all_months))
    expenses = by_month.get("Expense", pd.Series(0, index=all_months))

    positions = range(len(all_months))
    # Columns stay slim: with only a few months on screen they'd otherwise grow very wide.
    column_width = min(0.36, 0.015 * len(all_months) + 0.05)
    gap = column_width * 0.12  # a sliver of white between each pair of columns
    offset = (column_width + gap) / 2

    ax.bar([p - offset for p in positions], income, width=column_width,
           color=INCOME_COLOR, label="Income")
    ax.bar([p + offset for p in positions], expenses, width=column_width,
           color=EXPENSE_COLOR, label="Expenses")

    # Label every month for up to a year; beyond that, every few months so labels don't overlap.
    label_every = math.ceil(len(all_months) / 12)
    ax.set_xticks(list(positions)[::label_every])
    ax.set_xticklabels([month.strftime("%b\n%Y") for month in all_months][::label_every])

    ax.set_xlim(-0.6, len(all_months) - 0.4)  # keeps the spacing right even for a single month
    ax.set_ylim(0, max(income.max(), expenses.max()) * 1.1)  # headroom above the tallest column
    ax.yaxis.set_major_formatter(FuncFormatter(lambda value, _: money(value, cents=False)))
    ax.legend(loc="lower right", bbox_to_anchor=(1, 1), frameon=False, ncols=2,
              labelcolor=TEXT_PRIMARY)  # sits above the chart, clear of the columns
    style_axes(ax, "Income and expenses by month", grid_axis="y")


def draw_running_balance(ax, transactions):
    """A line showing net savings adding up over time (income counts up, expenses count down)."""
    signed = transactions["amount"].where(transactions["category"] == "Income",
                                          -transactions["amount"])
    balance = signed.groupby(transactions["date"]).sum().cumsum()

    # A step line: the balance stays flat between transactions, then jumps.
    ax.step(balance.index, balance.values, where="post", color=INCOME_COLOR, linewidth=2)
    ax.fill_between(balance.index, balance.values, step="post", color=INCOME_COLOR, alpha=0.1)
    ax.axhline(0, color=TEXT_SECONDARY, linewidth=1)

    # Label only the final value, just above the end of the line.
    ax.annotate(money(balance.iloc[-1], signed=True),
                xy=(balance.index[-1], balance.iloc[-1]), xytext=(0, 10),
                textcoords="offset points", ha="right", va="bottom", fontsize=10,
                color=TEXT_PRIMARY)
    ax.plot(balance.index[-1], balance.iloc[-1], "o", markersize=8, color=INCOME_COLOR,
            markeredgecolor=BACKGROUND, markeredgewidth=2)

    ax.yaxis.set_major_formatter(FuncFormatter(lambda value, _: money(value, cents=False)))
    # If everything happened on one day, show a month either side instead of a zero-width axis.
    if balance.index.min() == balance.index.max():
        day = balance.index[0]
        ax.set_xlim(day - pd.Timedelta(days=30), day + pd.Timedelta(days=30))

    ax.xaxis.set_major_locator(mdates.AutoDateLocator(maxticks=6))
    # Short periods show days ("Mar 14"); longer ones show months ("Mar 2025").
    start, end = (mdates.num2date(limit) for limit in ax.get_xlim())
    date_format = "%b %d" if (end - start).days <= 90 else "%b %Y"
    ax.xaxis.set_major_formatter(mdates.DateFormatter(date_format))
    style_axes(ax, "Running balance", grid_axis="y")


def draw_top_expenses(ax, transactions):
    """Horizontal bars for the biggest expense descriptions, largest at the top."""
    expenses = transactions[transactions["category"] == "Expense"]
    if expenses.empty:
        ax.axis("off")
        ax.text(0, 0.5, "No expenses in this period", color=TEXT_SECONDARY, transform=ax.transAxes)
        return

    by_description = (
        expenses.groupby(expenses["description"].str.strip().str.capitalize())["amount"]
        .sum()
        .sort_values(ascending=False)
    )

    # Keep the biggest few and add the rest together as "Other".
    if len(by_description) > TOP_EXPENSES:
        other = by_description.iloc[TOP_EXPENSES:].sum()
        by_description = by_description.iloc[:TOP_EXPENSES]
        by_description["Other"] = other

    by_description = by_description.iloc[::-1]  # matplotlib draws the first bar at the bottom
    ax.barh(by_description.index, by_description.values, height=0.6, color=EXPENSE_COLOR)

    # Write each amount just past the end of its bar.
    for row, amount in enumerate(by_description.values):
        ax.text(amount, row, f"  {money(amount)}", va="center", fontsize=9, color=TEXT_PRIMARY)

    ax.set_xlim(0, by_description.max() * 1.25)  # leave room for the labels
    ax.xaxis.set_major_formatter(FuncFormatter(lambda value, _: money(value, cents=False)))
    style_axes(ax, "Where the money went", grid_axis="x")


# ---- Helpers ------------------------------------------------------------------


def totals(transactions):
    """Returns (total income, total expenses) for a table of transactions."""
    income = transactions.loc[transactions["category"] == "Income", "amount"].sum()
    expenses = transactions.loc[transactions["category"] == "Expense", "amount"].sum()
    return income, expenses


def money(value, signed=False, cents=True):
    """Formats a number as dollars, e.g. 1234.5 -> "$1,234.50" (or "+$1,234.50" when signed)."""
    text = f"${abs(value):,.2f}" if cents else f"${abs(value):,.0f}"
    if value < 0:
        return "-" + text
    return ("+" + text) if signed and value > 0 else text


def style_axes(ax, title, grid_axis):
    """Gives a chart the shared look: a title, light gridlines and no box around it."""
    ax.set_title(title, loc="left", fontsize=12, fontweight="bold", color=TEXT_PRIMARY, pad=12)
    ax.set_facecolor(BACKGROUND)
    ax.grid(axis=grid_axis, color=GRID_COLOR, linewidth=1)
    ax.set_axisbelow(True)
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_color(GRID_COLOR)
    ax.tick_params(colors=TEXT_SECONDARY, length=0, labelsize=9)
