"""
Expense Tracker Application

This application provides a graphical user interface (GUI)
for efficient expense tracking. 
It offers features to manage and analyze financial data,
making it easier to monitor and control expenses.

It allows users to:
- Add, delete, and view expenses
- Generate monthly and category-wise reports
- Export expenses data to a CSV file
- Visualize expenses using bar and pie charts

The application uses SQLite as the backend database to store expense data.

Dependencies:
- sqlite3:              Provides an embedded database to store and manage expense records efficiently.
- csv:                  Enables exporting expense data into CSV files for external usage and sharing.
- datetime:             Handles date and time operations for accurate record-keeping and reporting.
- tkinter:              Used to create the graphical user interface, making the application user-friendly.
- ttk:                  Extends tkinter with themed widgets for improved interface aesthetics.
- tkcalendar:           Adds an interactive calendar widget to simplify date selection.
- matplotlib.pyplot:    Generates bar and pie charts to visualize expense trends effectively.
- pandas:               Assists with data manipulation and preparation for reports and visualizations.

Usage:
Run the script to launch the GUI and interact with the application.

Author: [Arayik Gevorgyan, Gor Barkhudaryan]
Date: [2024-11-19]
"""

import sqlite3
import csv
from datetime import datetime
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkcalendar import Calendar
import matplotlib.pyplot as plt
import pandas as pd

# python3 -u "/Users/arayik/Desktop/ProjectS3/expenses.py"

# Initialize and set up SQLite database
DB_FILE = "expenses.db"
conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()

# Create the expenses table if it doesn't exist
cursor.execute("""
    CREATE TABLE IF NOT EXISTS expenses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT NOT NULL,
        category TEXT NOT NULL,
        amount REAL NOT NULL
    )
""")
conn.commit()

def validate_date(date_text):
    """
    Validates the format of a date string.

    Args:
        date_text (str): The date string to validate in the format YYYY-MM-DD.

    Returns:
        bool: True if the date is valid, False otherwise.
    """
    try:
        datetime.strptime(date_text, "%Y-%m-%d")
        return True
    except ValueError:
        return False

def validate_amount(amount_text):
    """
    Validates if the given amount is a positive number.

    Args:
        amount_text (str): The amount as a string to validate.

    Returns:
        bool: True if the amount is a positive number, False otherwise.
    """
    try:
        return float(amount_text) > 0
    except ValueError:
        return False

def add_expense():
    """
    Adds a new expense to the database.

    Validates user input for date, category, and amount, then inserts the 
    expense into the SQLite database.

    Raises:
        ValueError: If any of the input fields are invalid.
    """

    date = date_entry.get()
    category = category_entry.get()
    amount = amount_entry.get()

    if not validate_date(date):
        status_label.config(text="Invalid date! Use YYYY-MM-DD format.", fg="red")
    elif not category:
        status_label.config(text="Category cannot be empty.", fg="red")
    elif not validate_amount(amount):
        status_label.config(text="Invalid amount! Enter a positive number.", fg="red")
    else:
        cursor.execute("INSERT INTO expenses (date, category, amount) VALUES (?, ?, ?)", (date, category, float(amount)))
        conn.commit()
        status_label.config(text="Expense added successfully!", fg="green")
        date_entry.delete(0, tk.END)
        category_entry.delete(0, tk.END)
        amount_entry.delete(0, tk.END)
        view_expenses()

def delete_expense():
    """
    Deletes the selected expense(s) from the database.

    This function removes the expense(s) that are currently selected in 
    the Treeview widget and updates the expense list view accordingly.
    """
    selected_items = expenses_tree.selection()
    if selected_items:
        for item in selected_items:
            item_id = expenses_tree.item(item, "values")[0]
            cursor.execute("DELETE FROM expenses WHERE id = ?", (item_id,))
        conn.commit()
        status_label.config(text="Selected expenses deleted successfully!", fg="green")
        view_expenses()

        # Check if all records are deleted and reset the ID sequence
        cursor.execute("SELECT COUNT(*) FROM expenses")
        count = cursor.fetchone()[0]
        if count == 0:
            cursor.execute("DELETE FROM sqlite_sequence WHERE name = 'expenses'")
            conn.commit()
    else:
        status_label.config(text="Please select an expense to delete!", fg="red")

# Function to delete all expenses and reset ID counter
def delete_all_expenses():
    """
    Deletes all expenses from the database and resets the ID counter.

    This function removes all records from the 'expenses' table and resets 
    the auto-increment sequence for the 'expenses' table to avoid gaps in 
    the ID numbering.
    """
    cursor.execute("DELETE FROM expenses")  # Delete all records
    cursor.execute("DELETE FROM sqlite_sequence WHERE name='expenses'")  # Reset the auto-increment counter
    conn.commit()
    status_label.config(text="All expenses deleted successfully!", fg="green")
    view_expenses()  # Refresh the expense view

# Function to view all expenses from the database
def view_expenses():
    """
    Displays all expenses in the Treeview widget and updates the total expense label.

    This function fetches all expenses from the database, populates the 
    Treeview widget with the expense records, and calculates the total expense 
    to be displayed.
    """
    cursor.execute("SELECT * FROM expenses")
    rows = cursor.fetchall()
    total_expense = sum(row[3] for row in rows)

    expenses_tree.delete(*expenses_tree.get_children())
    for row in rows:
        expenses_tree.insert("", tk.END, values=row)
    total_label.config(text=f"Total Expense: {total_expense:.2f}")

# Generate bar chart for monthly expenses
def generate_spending_chart():
    """
    Generates a bar chart showing monthly expenses.

    This function fetches total expenses grouped by month from the database 
    and creates a bar chart using Matplotlib to visualize the spending trend.
    """
    cursor.execute("SELECT strftime('%Y-%m', date) as month, SUM(amount) FROM expenses GROUP BY month")
    rows = cursor.fetchall()

    months = [row[0] for row in rows]
    totals = [row[1] for row in rows]

    plt.figure(figsize=(10, 6))
    plt.bar(months, totals, color='skyblue')
    plt.xlabel("Month")
    plt.ylabel("Total Expenses")
    plt.title("Monthly Spending Summary")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

# Generate pie chart for category-wise expenses
def generate_category_pie_chart():
    """
    Generates a pie chart showing the distribution of expenses by category.

    This function fetches expenses grouped by category from the database 
    and creates a pie chart using Matplotlib to visualize the category-wise 
    spending distribution.
    """
    cursor.execute("SELECT category, SUM(amount) FROM expenses GROUP BY category")
    rows = cursor.fetchall()

    categories = [row[0] for row in rows]
    amounts = [row[1] for row in rows]

    plt.figure(figsize=(8, 8))
    plt.pie(amounts, labels=categories, autopct='%1.1f%%', startangle=140)
    plt.title("Category-wise Spending Distribution")
    plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    plt.show()

def export_to_csv():
    """
    Exports the expenses data from the database to a CSV file.

    This function allows the user to select a location and filename to 
    save the expenses data in CSV format. It writes all the records from 
    the 'expenses' table into the CSV file.

    Raises:
        Exception: If an error occurs during the export process.
    """
    # Open a file dialog to save the CSV file
    file_path = filedialog.asksaveasfilename(
        defaultextension=".csv",
        filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
        title="Save CSV File"
    )

    if file_path:
        try:
            # Fetch data from the database
            cursor.execute("SELECT * FROM expenses")
            rows = cursor.fetchall()

            # Write to CSV
            with open(file_path, mode="w", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)
                writer.writerow(["ID", "Date", "Category", "Amount"])  # Header
                writer.writerows(rows)  # Data

            status_label.config(text="Data exported successfully!", fg="green")
        except Exception as e:
            status_label.config(text=f"Error exporting data: {e}", fg="red")

def generate_report():
    """
    Generates a detailed report of all expenses.

    This function creates a textual or CSV report containing all the expenses 
    stored in the database. It fetches all the data from the 'expenses' table, 
    formats it, and either displays it in the console or saves it to a file.

    The user will be prompted to choose whether they want to display the report 
    in the console or save it to a file.

    Args:
        None

    Raises:
        IOError: If there's an error writing to the report file.
        sqlite3.DatabaseError: If there's an issue querying the database.
    """
    start_date = start_calendar.get_date()
    end_date = end_calendar.get_date()

    cursor.execute("""
        SELECT * FROM expenses WHERE date BETWEEN ? AND ?
    """, (start_date, end_date))
    rows = cursor.fetchall()

    # Clear Treeview and populate with filtered data
    expenses_tree.delete(*expenses_tree.get_children())
    total = 0
    for row in rows:
        expenses_tree.insert("", tk.END, values=row)
        total += row[3]
    total_label.config(text=f"Total from {start_date} to {end_date}: {total:.2f}")
    status_label.config(text="Report generated for selected date range.", fg="green")

# Recommendation Function
def get_spending_insights():
    """
    Analyze the user's spending data and generate recommendations for saving money.
    
    Returns:
        List: A list of recommended actions based on spending patterns.
    """
    cursor.execute("SELECT category, SUM(amount) FROM expenses GROUP BY category")
    rows = cursor.fetchall()
    # Create a DataFrame to organize spending data
    df = pd.DataFrame(rows, columns=["Category", "Amount"])
    # Calculate total spending
    total_spent = df["Amount"].sum()

    # Generate recommendations based on spending categories
    recommendations = []

    # If spending on dining out is more than 20% of total spending, suggest saving
    dining_spent = df[df["Category"].str.contains("Dining Out", case=False, na=False)]["Amount"].sum()
    if dining_spent > total_spent * 0.2:
        recommendations.append("Consider reducing spending on dining out to save more.")

    # If spending on entertainment is more than 15% of total spending, suggest saving
    entertainment_spent = df[df["Category"].str.contains("Entertainment", case=False, na=False)]["Amount"].sum()
    if entertainment_spent > total_spent * 0.15:
        recommendations.append("Think about cutting down on entertainment expenses.")

    # Suggest saving tips based on high spending categories
    if not recommendations:
        recommendations.append("You're doing great! Keep up the good work.")
    return recommendations

# Set up main window
root = tk.Tk()
root.title("Expense Tracker")

# Create a Canvas widget to hold all the content
canvas = tk.Canvas(root)
canvas.pack(side="left", fill="both", expand=True)

# Create a vertical scrollbar linked to the Canvas
scrollbar = tk.Scrollbar(root, orient="vertical", command=canvas.yview)
scrollbar.pack(side="right", fill="y")

# Configure the canvas to use the scrollbar
canvas.configure(yscrollcommand=scrollbar.set)

# Create a Frame inside the Canvas to hold all widgets
frame = tk.Frame(canvas)
canvas.create_window((0, 0), window=frame, anchor="nw")

# Bind the frame to the canvas to allow scrolling
frame.bind(
    "<Configure>",
    lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
)

# Entry fields for adding expenses
date_label = tk.Label(frame, text="Date (YYYY-MM-DD):")
date_label.grid(row=0, column=0, padx=10, pady=10)
date_entry = tk.Entry(frame)
date_entry.grid(row=0, column=1)

category_label = tk.Label(frame, text="Category:")
category_label.grid(row=1, column=0, padx=10, pady=10)
category_entry = tk.Entry(frame)
category_entry.grid(row=1, column=1)

amount_label = tk.Label(frame, text="Amount:")
amount_label.grid(row=2, column=0, padx=10, pady=10)
amount_entry = tk.Entry(frame)
amount_entry.grid(row=2, column=1)

# Buttons for actions
add_button = tk.Button(frame, text="Add Expense", command=add_expense)
add_button.grid(row=3, column=1, padx=10, pady=10)

# Expense list view
columns = ("ID", "Date", "Category", "Amount")
expenses_tree = ttk.Treeview(frame, columns=columns, show="headings", selectmode="extended")
for col in columns:
    expenses_tree.heading(col, text=col)

# Create a Scrollbar for the Treeview
treeview_scrollbar = tk.Scrollbar(frame, orient="vertical", command=expenses_tree.yview)
expenses_tree.configure(yscrollcommand=treeview_scrollbar.set)

# Grid the Treeview and Scrollbar
expenses_tree.grid(row=4, column=0, columnspan=2, padx=10, pady=10)
treeview_scrollbar.grid(row=4, column=2, sticky="ns", padx=5, pady=10)

delete_button = tk.Button(frame, text="Delete Expense", command=delete_expense)
delete_button.grid(row=5, column=0, padx=10, pady=10)

# Delete all button
delete_all_button = tk.Button(frame, text="Delete All Expenses", command=delete_all_expenses)
delete_all_button.grid(row=5, column=1, padx=10, pady=10)

# Labels for status and totals
status_label = tk.Label(frame, text="")
status_label.grid(row=7, column=0, columnspan=2)

total_label = tk.Label(frame, text="Total Expense: 0.00")
total_label.grid(row=8, column=0, columnspan=2)

# Calendar for selecting start and end dates
start_date_label = tk.Label(frame, text="Select Start Date:")
start_date_label.grid(row=9, column=0, padx=10, pady=10)

start_calendar = Calendar(frame, selectmode="day", date_pattern="yyyy-mm-dd")
start_calendar.grid(row=10, column=0, padx=10, pady=10)

end_date_label = tk.Label(frame, text="Select End Date:")
end_date_label.grid(row=9, column=1, padx=10, pady=10)

end_calendar = Calendar(frame, selectmode="day", date_pattern="yyyy-mm-dd")
end_calendar.grid(row=10, column=1, padx=10, pady=10)

# Buttons for monthly reports and charts
report_button = tk.Button(frame, text="Generate Report", command=generate_report)
report_button.grid(row=11, column=1, padx=10, pady=10)

chart_button = tk.Button(frame, text="Show Spending Chart", command=generate_spending_chart)
chart_button.grid(row=12, column=0, padx=10, pady=10)

pie_chart_button = tk.Button(frame, text="Show Category Pie Chart", command=generate_category_pie_chart)
pie_chart_button.grid(row=13, column=0, padx=10, pady=10)

export_button = tk.Button(frame, text="Export to CSV", command=export_to_csv)
export_button.grid(row=14, column=0, padx=10, pady=10)

category_label = tk.Label(frame, text="")
category_label.grid(row=15, column=0, columnspan=2, pady=10)

# Function to display AI recommendations
def display_recommendations():
    """
    Display the spending recommendations to the user.
    """
    recommendations = get_spending_insights()
    recommendations_text = "\n".join(recommendations)
    status_label.config(text=f"Recommendations:\n{recommendations_text}", fg="green")

# Add a button to show recommendations
recommendations_button = tk.Button(frame, text="Get Recommendations", command=display_recommendations)
recommendations_button.grid(row=15, column=0, padx=10, pady=10)

view_expenses()

root.mainloop()

conn.close()