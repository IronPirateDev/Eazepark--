import tkinter as tk
from tkcalendar import Calendar
import mysql.connector as ms

global formatted_date  # Declare formatted_date as a global variable
formatted_date = ""

def get_selected_date():
    global formatted_date
    selected_date = cal.get_date()
    formatted_date = format_date(selected_date)
    root.destroy()
    fetch_data_from_database()

def format_date(date_str):
    formatted_date = date_str.split('/')
    formatted_date = f"20{int(formatted_date[2]):02d}-{int(formatted_date[0]):02d}-{int(formatted_date[1]):02d}"
    return formatted_date

def fetch_data_from_database():
    global formatted_date  # Declare formatted_date as a global variable
    db = ms.connect(
        host="localhost",
        user="root",
        password="dpsbn",
        database="cars"
    )
    cursor = db.cursor()
    q1 = 'select * from rep where timestamp=%s'
    cursor.execute(q1, (formatted_date,))
    a = cursor.fetchall()
    nmfl = 'F:/Report Generator/'+str(formatted_date) + '.csv'

    import csv
    with open(nmfl, 'w', newline='') as file: 
        wo = csv.writer(file)
        for i in a:
            wo.writerow(list(i))
        
        qqqq = 'SELECT COUNT(*) FROM rep WHERE timestamp=%s'
        cursor.execute(qqqq, (formatted_date,))
        total_count = cursor.fetchone()[0]
        wo.writerow([])  # Add an empty row for spacing
        wo.writerow(["Total Count:", total_count])

        qqqq = 'SELECT SUM(money_paid) FROM rep WHERE timestamp=%s'
        cursor.execute(qqqq, (formatted_date,))
        total_money_paid = cursor.fetchone()[0]
        wo.writerow(["Total Money Paid:", total_money_paid])

    db.close()

root = tk.Tk()
root.title("Calendar")
cal = Calendar(root, selectmode="day")
cal.pack(padx=20, pady=20)
btn = tk.Button(root, text="Generate Report", command=get_selected_date)
btn.pack(pady=10)
root.mainloop()
