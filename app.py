# create a student information form name, gender, dob, languages known, academic pointer (scale), branch selection(combo box)  and submit button then display all the information in textbox using a tkinter.
import tkinter as tk
from tkinter import ttk

def submit_form():
    # Get values from the form fields
    name = name_entry.get()
    gender = gender_var.get()
    dob = dob_entry.get()
    # languages = ", ".join(language_vars[var].get() for var in language_vars)
    pointer = pointer_scale.get()
    branch = branch_combo.get()

    # Display the information in the text box
    info_text.delete(1.0, tk.END)
    info_text.insert(tk.END, f"Name: {name}\n")
    info_text.insert(tk.END, f"Gender: {gender}\n")
    info_text.insert(tk.END, f"Date of Birth: {dob}\n")
    # info_text.insert(tk.END, f"Languages Known: {languages}\n")
    info_text.insert(tk.END, f"Academic Pointer: {pointer}\n")
    info_text.insert(tk.END, f"Branch: {branch}\n")

root = tk.Tk()
root.title("Student Information Form")

# Name field
tk.Label(root, text="Name:").grid(row=0, column=0)
name_entry = tk.Entry(root)
name_entry.grid(row=0, column=1)

# Gender field
tk.Label(root, text="Gender:").grid(row=1, column=0)
gender_var = tk.StringVar(value="Male")
male_radio = tk.Radiobutton(root, text="Male", variable=gender_var, value="Male")
male_radio.grid(row=1, column=1)
female_radio = tk.Radiobutton(root, text="Female", variable=gender_var, value="Female")
female_radio.grid(row=2, column=1)

# Date of Birth field
tk.Label(root, text="Date of Birth:").grid(row=3, column=0)
dob_entry = tk.Entry(root)
dob_entry.grid(row=3, column=1)


# Academic Pointer field
tk.Label(root, text="Academic Pointer:").grid(row=4, column=0)
pointer_scale = tk.Scale(root, from_=0, to=10, orient=tk.HORIZONTAL, resolution=0.1)
pointer_scale.grid(row=4, column=1)

# Branch Selection field
tk.Label(root, text="Branch:").grid(row=5, column=0)
branch_combo = ttk.Combobox(root, values=["Computer Science(Data science)", "Electrical Engineering", "Mechanical Engineering", "Civil Engineering"])
branch_combo.grid(row=5, column=1)

# Submit button
submit_button = tk.Button(root, text="Submit", command=submit_form)
submit_button.grid(row=6, column=0, columnspan=2)

# Display area for information
info_text = tk.Text(root, width=40, height=10)
info_text.grid(row=7, column=0, columnspan=2)

root.mainloop()




