from datetime import datetime
import re
from tkinter import messagebox
import mysql.connector
import tkinter as tk
from tkinter import ttk, messagebox
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="khushbu@060626",
    database="paper_inventory_db"
)

cursor = conn.cursor()
root = tk.Tk()
root.title("User Registration")
root.geometry("500x600")
root.resizable(False, False)
tk.Label(root, text="User Registration Form",
         font=("Arial", 16, "bold")).pack(pady=10)

# User ID
#tk.Label(root, text="User ID").pack()
#user_id_entry = tk.Entry(root, width=30)
#user_id_entry.pack()

# Username
tk.Label(root, text="Username").pack()
username_entry = tk.Entry(root, width=30)
username_entry.pack()
#username validation


# Email
tk.Label(root, text="Email").pack()
email_entry = tk.Entry(root, width=30)
email_entry.pack()

# Display Name
tk.Label(root, text="Display Name").pack()
display_name_entry = tk.Entry(root, width=30)
display_name_entry.pack()

# Employee ID
tk.Label(root, text="Employee ID").pack()
employee_id_entry = tk.Entry(root, width=30)
employee_id_entry.pack()

# Password
tk.Label(root, text="Password").pack()
password_entry = tk.Entry(root, show="*", width=30)
password_entry.pack()

# Confirm Password
tk.Label(root, text="Confirm Password").pack()
confirm_password_entry = tk.Entry(root, show="*", width=30)
confirm_password_entry.pack()


#active user
active_var = tk.IntVar()
tk.Checkbutton(
    root,
    text="Active User",
    variable=active_var
).pack(pady=5)
tk.Label(root, text="Security Questions").pack()

security_combo = ttk.Combobox(root, width=27 , state="readonly")

security_combo["values"] = (
    "What is your date of birth?",
    "What is your favourite color?",
    "What is your first school name?",
    "What is your pet name?"
)
security_combo.current(0)

security_combo.pack( )


tk.Label(root, text="Security Answers").pack()

security_answer_entry = tk.Entry(root, width=30)
security_answer_entry.pack()

def register():
    username = username_entry.get().strip()

    if username == "":
       messagebox.showerror("Error", "Username can't be empty")
       return

    pattern = r"^[a-zA-Z0-9]+$"

    if not re.match(pattern, username):
       messagebox.showerror(
        "Error",
        "Username must contain only letters (A-Z, a-z)"
    )
       return
    print("Username passed")

   
    email = email_entry.get().strip()
    #pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    #pattern = r"^[a-zA-Z0-9]+[._-][a-zA-Z0-9._-]*@(gmail\.com|yahoo\.com|outlook\.com|hotmail\.com|icloud\.com)$"
   # pattern = r"^[a-zA-Z0-9._%+-]+@(gmail\.com|yahoo\.com|outlook\.com|hotmail\.com|icloud\.com)$"
    pattern = r"^[a-zA-Z0-9._]+@[a-zA-Z0-9.]+\.(com|in|org)$"

   # pattern = r"^[a-zA-Z0-9]+@gmail\.com$"
    if not re.match(pattern, email):
       messagebox.showerror("Error",
      "Enter a valid Gmail address."
       )
       return
    print("Email passed")
    display_name= display_name_entry.get().strip()

    if display_name == "":
       messagebox.showerror("Error", "display_name can't be empty")
       return

    pattern = r"^[a-zA-Z_]+$"
    #pattern = r"^[a-zA-Z0-9]+[._-][a-zA-Z0-9._-]*@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    if not re.match(pattern, display_name):
       messagebox.showerror(
        "Error",
        " display name must contain only letters (A-Z, a-z)"
    )
       return

    print("Display Name passed")


  
    employee_id = employee_id_entry.get()
    # employee_id validation
    employee_id=employee_id_entry.get().strip()

    if not employee_id.isdigit():
        messagebox. showerror("error","employee_id must contain only numbers")
        return
    print("Employee ID passed")
    password = password_entry.get()
    # password validation
    password=password_entry.get().strip()

    if password=="":
        messagebox.showerror("error","password is required!")
        return
    print("Password passed")
    confirm_password = confirm_password_entry.get()
    #confirm_password validation
    confirm_password=confirm_password_entry.get().strip()

    if confirm_password=="":
        messagebox.showerror("error","please confirm password!")
        return
    print("Confirm Password passed")
    active = active_var.get()
    #active validation
    
    if active==0:
        messagebox.showerror("error","please active the user")
        return
    print("Active User passed")
    security_question = security_combo.get()
    

    if security_question==" select security question":
        messagebox.showerror("error","please select the security questions")
        return
    print("Security Question passed")
    security_question = security_combo.get()
    security_answer = security_answer_entry.get().strip()
    if security_answer == "":
       messagebox.showerror(
        "Error",
        "Please enter a security answer"
    )
       return
    print("Question:", security_question)
    print("Answer:", security_answer)
    #validation date of birth
    if security_question == "What is your date of birth?":
       try:
        dob = datetime.strptime(security_answer, "%d/%m/%Y")
        today = datetime.now()

        # Future date check
        if dob > today:
            messagebox.showerror(
                "Error",
                "Date of birth cannot be in the future"
            )
            return

        # Calculate age
        age = today.year - dob.year
        if (today.month, today.day) < (dob.month, dob.day):
            age -= 1

        # Minimum age check
        if age < 18:
            messagebox.showerror(
                "Error",
                "Employee must be at least 18 years old"
            )
            return

        # Maximum age check
        if age > 100:
            messagebox.showerror(
                "Error",
                "Age cannot be more than 100 years"
            )
            return

       except ValueError:
        messagebox.showerror(
            "Error",
            "Please enter a valid date "
        )
        return
    # Favourite Color validation
    elif security_question == "What is your favourite color?":
     if not re.match(r"^[A-Za-z]+$", security_answer):
        messagebox.showerror(
            "Error",
            "Color should contain only letters"
        )
        return

# School Name validation
    elif security_question == "What is your first school name?":
     if not re.match(r"^[A-Za-z ]+$", security_answer):
        messagebox.showerror(
            "Error",
            "School name should contain only letters and spaces"
        )
        return

# Pet Name validation
    elif security_question == "What is your pet name?":
     if not re.match(r"^[A-Za-z]+$", security_answer):
        messagebox.showerror(
            "Error",
            "Pet name should contain only letters"
        )
        return
     print("Security Answer passed")

    if username == "" or employee_id == "" or password == "":
        messagebox.showerror("Error", "Fill all required fields")
        return
    print("All validations passed")

    try:

        cursor.execute(
            "SELECT * FROM users WHERE employee_id=%s",
            (employee_id,)
        )

        if cursor.fetchone():
            messagebox.showerror(
                "Error",
                "Employee ID already exists"
            )
            return

        if password != confirm_password:
            messagebox.showerror(
                "Error",
                "Passwords do not match"
            )
            return

        cursor.execute(
            """
            INSERT INTO users
            (username, password,
             email, display_name,
             employee_id, active,
             security_question,
             security_answer)

            VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
            """,
            (
                username,
                password,
                email,
                display_name,
                employee_id,
                active,
                security_question,
                security_answer
            )
        )

        conn.commit()

        messagebox.showinfo(
            "Success",
            "Registration Successful"
        )

    except Exception as e:
        messagebox.showerror(
            "Database Error",
            str(e)
        )
tk.Button(
    root,
    text="Register",
    command=register
).pack(pady=20)

root.mainloop()