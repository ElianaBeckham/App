# ============================================================
# Expense Tracker App
# Built with Python + Streamlit
# ============================================================
# What this app does:
#   1. Lets you enter an expense (amount, category, date, description)
#   2. Saves every expense in a pandas DataFrame (a table)
#   3. Shows all expenses in a table
#   4. Shows the total of all expenses
#   5. Shows totals for each category
#   6. Draws a bar chart of spending by category
#   7. Has a "Clear All" button to erase everything
#   8. Refuses amounts that are zero or negative
# ============================================================

# --- Imports: the tools (packages) this app needs ---
import datetime            # built into Python, used for today's date
import pandas as pd        # for storing expenses in a table (DataFrame)
import streamlit as st     # for turning this code into a web app

# --- The list of categories for the dropdown menu ---
CATEGORIES = ["Food", "Transport", "Entertainment", "Bills", "Other"]

# --- Page setup: the title in the browser tab and the page layout ---
st.set_page_config(page_title="Expense Tracker", page_icon="💰")

st.title("💰 Expense Tracker")
st.write(
    "Add your expenses below. The app keeps a running table, "
    "adds up your totals, and shows where your money goes."
)

# ------------------------------------------------------------
# STORING THE DATA
# ------------------------------------------------------------
# Streamlit re-runs this whole file from top to bottom every time
# you click a button. Normal variables would get wiped out each time.
# "st.session_state" is a special place that REMEMBERS data between
# re-runs, so we keep our expenses table there.
if "expenses" not in st.session_state:
    # Start with an empty table that has these 4 columns
    st.session_state.expenses = pd.DataFrame(
        columns=["Date", "Category", "Description", "Amount"]
    )

# ------------------------------------------------------------
# INPUT FORM: where the user types in a new expense
# ------------------------------------------------------------
# A "form" groups the inputs so nothing happens until you press Submit.
# clear_on_submit=True empties the boxes after each expense is added.
st.header("Add an Expense")

with st.form("expense_form", clear_on_submit=True):
    # Amount: a number box. min_value=0.0 stops typing negatives with
    # the arrows, and we double-check below anyway.
    amount = st.number_input(
        "Amount ($)", min_value=0.0, step=1.0, format="%.2f"
    )

    # Category: a dropdown menu with our 5 choices
    category = st.selectbox("Category", CATEGORIES)

    # Date: a calendar date picker that starts on today's date
    date = st.date_input("Date", value=datetime.date.today())

    # Description: a short text box
    description = st.text_input("Description", placeholder="e.g. Lunch with friends")

    # The button that sends the form
    submitted = st.form_submit_button("Add Expense")

# ------------------------------------------------------------
# VALIDATION: check the input before saving it
# ------------------------------------------------------------
if submitted:
    if amount <= 0:
        # Error message instead of saving a bad amount
        st.error("❌ The amount must be a positive number (greater than $0).")
    else:
        # Build a one-row table for the new expense...
        new_row = pd.DataFrame(
            [{
                "Date": date,
                "Category": category,
                "Description": description.strip() or "(no description)",
                "Amount": round(float(amount), 2),
            }]
        )
        # ...and stick it onto the bottom of the saved table
        st.session_state.expenses = pd.concat(
            [st.session_state.expenses, new_row], ignore_index=True
        )
        st.success(f"✅ Added ${amount:,.2f} for {category}.")

# A shorter name for the saved table so the code below is easier to read
expenses = st.session_state.expenses

# ------------------------------------------------------------
# SHOWING THE RESULTS
# ------------------------------------------------------------
st.header("Your Expenses")

if expenses.empty:
    # Nothing has been added yet
    st.info("No expenses yet. Add one above to get started!")
else:
    # Make sure the Amount column is treated as numbers (not text)
    expenses["Amount"] = pd.to_numeric(expenses["Amount"])

    # --- 1. Table of every expense ---
    st.dataframe(
        expenses,
        width="stretch",
        hide_index=True,
        column_config={
            "Amount": st.column_config.NumberColumn("Amount", format="$%.2f")
        },
    )

    # --- 2. Total of all expenses ---
    total = expenses["Amount"].sum()
    st.metric("Total Spent", f"${total:,.2f}")

    # --- 3. Totals for each category ---
    # groupby("Category") puts rows with the same category together,
    # then .sum() adds up the amounts inside each group.
    by_category = (
        expenses.groupby("Category")["Amount"]
        .sum()
        .reindex(CATEGORIES, fill_value=0.0)  # show all 5, even if $0
    )

    st.subheader("Spending by Category")
    category_table = by_category.reset_index()
    category_table.columns = ["Category", "Total"]
    st.dataframe(
        category_table,
        width="stretch",
        hide_index=True,
        column_config={
            "Total": st.column_config.NumberColumn("Total", format="$%.2f")
        },
    )

    # --- 4. Bar chart of spending by category ---
    st.bar_chart(by_category, x_label="Category", y_label="Amount ($)")

    # ------------------------------------------------------------
    # CLEAR ALL BUTTON: wipes every expense
    # ------------------------------------------------------------
    if st.button("🗑️ Clear All Expenses"):
        st.session_state.expenses = pd.DataFrame(
            columns=["Date", "Category", "Description", "Amount"]
        )
        st.rerun()  # reload the page so the empty table shows right away
