import tkinter as tk
from tkinter import messagebox
from tkinter.scrolledtext import ScrolledText
from tkcalendar import DateEntry
import json
from datetime import datetime, timedelta


# Load excluded dates from JSON file
def load_excluded_dates(filename="excluded_dates.json"):
    try:
        with open(filename, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

# Save excluded dates to JSON file
def save_excluded_dates(dates, filename="excluded_dates.json"):
    with open(filename, "w") as f:
        json.dump(dates, f)

# Initialize excluded dates
excluded_dates = load_excluded_dates()

def calculate_course_schedule(num_sessions, start_date, selected_days):
    try:
        current_date = datetime.strptime(start_date, "%d-%m-%Y")
    except ValueError:
        messagebox.showerror("Error", f'Invalid start date: {start_date}.')
        return []

    # default days_index = {"mo": 0, "tu": 1, "we": 2, "th": 3, "fr": 4, "sa": 5, "su": 6}
    # my system days_index = {"su": 0, "mo": 1, "tu": 2, "we": 3, "th": 4, "fr": 5, "sa": 6}
    # adjust to convert my index to be equal to sys index - e.g.: my "we" is 3 -> (3 + 6) mod 7 = 2 (sys "we")    
    # Adjust the selected_days to map correctly with weekday() 
    adjusted_days = [(day + 6) % 7 for day in selected_days]
    
    schedule_dates = []
    while len(schedule_dates) < num_sessions:
        if current_date.weekday() in adjusted_days:
            if current_date.strftime("%d-%m-%Y") not in excluded_dates:
                schedule_dates.append(current_date.strftime("%d-%m-%Y"))
        current_date += timedelta(days=1)
    return schedule_dates

def submit():
    # Validate and retrieve the number of sessions
    try:
        num_sessions = int(num_sessions_var.get())
    except ValueError:
        messagebox.showerror("Error", "Please enter a valid number of sessions.")
        return

    # Get the start date in the correct format
    start_date = start_date_var.get_date().strftime("%d-%m-%Y")

    # Get the selected days of the week
    selected_days = []
    for day, var in day_vars.items():
        if var.get() == 1:
            selected_days.append(day)

    # Check if at least one day is selected
    if not selected_days:
        messagebox.showerror("Error", "Please select at least one day of the week.")
        return

    # Calculate the course schedule dates
    schedule_dates = calculate_course_schedule(num_sessions, start_date, selected_days)
    if schedule_dates:
        result_text.config(state=tk.NORMAL)
        result_text.delete(1.0, tk.END)
        result_text.insert(tk.END, "Session Number\t\tDate\t\tWeek Day\n")
        for i, date in enumerate(schedule_dates, 1):
            weekday = datetime.strptime(date, "%d-%m-%Y").strftime("%A")
            result_text.insert(tk.END, f"{i}\t\t{date}\t\t{weekday}\n")
        result_text.config(state=tk.DISABLED)

def add_excluded_date():
    # Add the selected date to the excluded dates list
    selected_date = cal.get_date().strftime("%d-%m-%Y")
    if selected_date not in excluded_dates:
        excluded_dates.append(selected_date)
        excluded_dates_listbox.insert(tk.END, selected_date)
        save_excluded_dates(excluded_dates)
    else:
        messagebox.showinfo("Info", f"{selected_date} is already in the excluded dates.")

def remove_excluded_date():
    # Remove the selected date from the excluded dates list
    selected_index = excluded_dates_listbox.curselection()
    if selected_index:
        selected_date = excluded_dates_listbox.get(selected_index)
        excluded_dates.remove(selected_date)
        excluded_dates_listbox.delete(selected_index)
        save_excluded_dates(excluded_dates)

# Initialize the main window
root = tk.Tk()
root.title("Course Schedule Calculator")
root.geometry("770x680")
root.configure(bg="lightblue")

# Variables
num_sessions_var = tk.StringVar()
start_date_var = tk.StringVar()
day_vars = {i: tk.IntVar() for i in range(7)}

# Inputs Section
inputs_frame = tk.Frame(root, padx=10, pady=10)
inputs_frame.grid(row=0, column=0, padx=10, pady=10, sticky=tk.NW)

tk.Label(inputs_frame, text="Number of Sessions:", font=("Verdana", 11)).grid(row=0, column=0, sticky=tk.W, pady=5)
num_sessions_entry = tk.Entry(inputs_frame, textvariable=num_sessions_var, font=("Verdana", 11))
num_sessions_entry.grid(row=0, column=1, pady=5)
num_sessions_entry.focus()

tk.Label(inputs_frame, text="Start Date:", font=("Verdana", 11)).grid(row=1, column=0, sticky=tk.W, pady=5)
start_date_var = DateEntry(inputs_frame, width=12, background='darkgreen', foreground='white', borderwidth=2, 
                           date_pattern="dd-mm-yyyy")
start_date_var.grid(row=1, column=1, pady=5)

tk.Label(inputs_frame, text="Days of the Week:", font=("Verdana", 11)).grid(row=2, column=0, sticky=tk.W, pady=5)
days_frame = tk.Frame(inputs_frame)
days_frame.grid(row=2, column=1, sticky=tk.W, pady=5)
day_names = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
for i, day_name in enumerate(day_names):
    tk.Checkbutton(days_frame, text=day_name, variable=day_vars[i], font=("Arial", 10)).grid(row=i, column=0, sticky=tk.W)

tk.Button(inputs_frame, text="Submit", command=submit, font=("Verdana", 11)).grid(row=3, column=0, columnspan=2, pady=11)

# Excluded Dates Section
excluded_frame = tk.Frame(root, padx=10, pady=10)
excluded_frame.grid(row=0, column=1, padx=10, pady=10, sticky=tk.NW)

tk.Label(excluded_frame, text="Excluded Dates:", font=("Verdana", 11)).grid(row=0, column=0, sticky=tk.W, pady=5)
cal = DateEntry(excluded_frame, width=12, background='darkgreen', foreground='white', borderwidth=2, 
                date_pattern="dd-mm-yyyy")
cal.grid(row=0, column=1, sticky=tk.W, pady=5)
tk.Button(excluded_frame, text="Add Date", command=add_excluded_date, font=("Verdana", 11)).grid(row=0, column=2, 
                                                                                               sticky=tk.W, padx=10, 
                                                                                               pady=10)

excluded_dates_listbox = tk.Listbox(excluded_frame, height=11, font=("Verdana", 11))
excluded_dates_listbox.grid(row=1, column=0, columnspan=2, sticky=tk.W+tk.E, pady=5)
excluded_dates_scrollbar = tk.Scrollbar(excluded_frame, orient="vertical")
excluded_dates_scrollbar.config(command=excluded_dates_listbox.yview)
excluded_dates_listbox.config(yscrollcommand=excluded_dates_scrollbar.set)
excluded_dates_scrollbar.grid(row=1, column=2, sticky=tk.N+tk.S+tk.W, pady=5)
tk.Button(excluded_frame, text="Remove Date", command=remove_excluded_date, font=("Verdana", 11)).grid(row=2, 
                                                                                                     column=0, 
                                                                                                     columnspan=3, 
                                                                                                     pady=3)

# Populate listbox with initial excluded dates
for date in excluded_dates:
    excluded_dates_listbox.insert(tk.END, date)

# Results Section
results_frame = tk.Frame(root, padx=10, pady=10)
results_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky=tk.W+tk.E)

result_text = ScrolledText(results_frame, height=15, width=70, state=tk.DISABLED, font=("Verdana", 11))
result_text.pack(fill=tk.BOTH, expand=True)

root.mainloop()