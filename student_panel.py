import tkinter as tk
from tkinter import messagebox
import sqlite3
import sys

# -- Get student email from command-line argument --
if len(sys.argv) < 2:
    print("Error: No student email provided.")
    sys.exit(1)

student_email = sys.argv[1]

# -- Connect to DB --
conn = sqlite3.connect("hostel.db")
cur = conn.cursor()

# -- GUI Setup --
root = tk.Tk()
root.title("Student Panel")
root.state('zoomed')  # Maximized window
root.resizable(False, False)

screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

# --- Gradient background ---
def draw_gradient(canvas, color1, color2):
    width = screen_width
    height = screen_height
    r1, g1, b1 = root.winfo_rgb(color1)
    r2, g2, b2 = root.winfo_rgb(color2)
    r_ratio = float(r2 - r1) / height
    g_ratio = float(g2 - g1) / height
    b_ratio = float(b2 - b1) / height
    for i in range(height):
        nr = int(r1 + (r_ratio * i))
        ng = int(g1 + (g_ratio * i))
        nb = int(b1 + (b_ratio * i))
        color = "#%04x%04x%04x" % (nr, ng, nb)
        canvas.create_line(0, i, width, i, fill=color)

canvas = tk.Canvas(root, width=screen_width, height=screen_height, highlightthickness=0)
canvas.place(x=0, y=0)
draw_gradient(canvas, "#a1c4fd", "#c2e9fb")  # blue gradient

# --- Card Frame ---
main_frame = tk.Frame(root, bg="#fff", bd=0, relief="ridge", highlightbackground="#3b82f6", highlightthickness=2)
main_frame.place(relx=0.5, rely=0.5, anchor="center", width=500, height=600)

tk.Label(main_frame, text="🎓 Student Dashboard", font=("Segoe UI", 20, "bold"), fg="#2563eb", bg="#fff").pack(pady=20)

# --- Welcome by full name ---
cur.execute("SELECT name FROM users WHERE email=?", (student_email,))
student_name = cur.fetchone()
if student_name:
    welcome_text = f"Welcome, {student_name[0]}!"
else:
    welcome_text = "Welcome!"

tk.Label(main_frame, text=welcome_text, font=("Segoe UI", 14, "bold"), fg="#334155", bg="#fff").pack(pady=5)

# === Features ===

def view_room():
    cur.execute("SELECT floor, seater FROM users WHERE email=?", (student_email,))
    result = cur.fetchone()
    if not result:
        messagebox.showerror("Error", "Student info not found.")
        return
    floor, seater = result
    if seater == "Single":
        messagebox.showinfo("Room Info", "You are in a single seater room.")
        return

    win = tk.Toplevel(root)
    win.title("Roommates")
    win.geometry("400x300")
    win.configure(bg="#e0e7ef")
    tk.Label(win, text=f"{seater} Seater Roommates (Floor {floor})", font=("Segoe UI", 14, "bold"), bg="#e0e7ef", fg="#2563eb").pack(pady=10)
    cur.execute("SELECT name, phone FROM users WHERE floor=? AND seater=? AND email!=?", (floor, seater, student_email))
    roommates = cur.fetchall()
    if not roommates:
        tk.Label(win, text="No roommates found.", bg="#e0e7ef", fg="#2563eb").pack(pady=10)
    else:
        for idx, (name, phone) in enumerate(roommates):
            tk.Label(win, text=f"{idx+1}. {name} | {phone}", bg="#e0e7ef", fg="#2563eb").pack(anchor="w", padx=10, pady=2)

def make_complaint():
    def submit():
        text = complaint.get().strip()
        if not text:
            messagebox.showerror("Error", "Complaint cannot be empty.")
            return
        cur.execute("INSERT INTO complaints (email, complaint) VALUES (?, ?)", (student_email, text))
        conn.commit()
        messagebox.showinfo("Done", "Complaint submitted.")
        win.destroy()

    win = tk.Toplevel(root)
    win.title("Make Complaint")
    win.geometry("300x150")
    win.configure(bg="#e0e7ef")
    tk.Label(win, text="Enter complaint:", bg="#e0e7ef", fg="#2563eb").pack(pady=10)
    complaint = tk.StringVar()
    tk.Entry(win, textvariable=complaint, width=35, bg="#fff", fg="#232526").pack()
    tk.Button(win, text="Submit", command=submit, bg="#e67e22", fg="white").pack(pady=10)

def request_leave():
    def submit():
        text = reason.get().strip()
        if not text:
            messagebox.showerror("Error", "Reason cannot be empty.")
            return
        cur.execute("INSERT INTO leaves (email, reason) VALUES (?, ?)", (student_email, text))
        conn.commit()
        messagebox.showinfo("Done", "Leave requested.")
        win.destroy()

    win = tk.Toplevel(root)
    win.title("Request Leave")
    win.geometry("300x150")
    win.configure(bg="#e0e7ef")
    tk.Label(win, text="Leave Reason:", bg="#e0e7ef", fg="#2563eb").pack(pady=10)
    reason = tk.StringVar()
    tk.Entry(win, textvariable=reason, width=35, bg="#fff", fg="#232526").pack()
    tk.Button(win, text="Submit", command=submit, bg="#2ecc71", fg="white").pack(pady=10)

def view_complaints():
    win = tk.Toplevel(root)
    win.title("Your Complaints")
    win.geometry("400x350")
    win.configure(bg="#e0e7ef")
    tk.Label(win, text="Your Complaints", font=("Segoe UI", 14, "bold"), bg="#e0e7ef", fg="#2563eb").pack(pady=10)
    try:
        cur.execute("ALTER TABLE complaints ADD COLUMN viewed INTEGER DEFAULT 0")
    except sqlite3.OperationalError:
        pass
    cur.execute("SELECT complaint, viewed FROM complaints WHERE email=?", (student_email,))
    complaints = cur.fetchall()
    if not complaints:
        tk.Label(win, text="No complaints submitted.", bg="#e0e7ef", fg="#2563eb").pack(pady=10)
    for idx, (msg, viewed) in enumerate(complaints):
        status = "Viewed" if viewed else "Unviewed"
        tk.Label(win, text=f"{idx+1}. {msg} [{status}]", bg="#e0e7ef", fg="#2563eb", anchor="w").pack(fill="x", padx=10, pady=2)

def view_leaves():
    win = tk.Toplevel(root)
    win.title("Your Leave Requests")
    win.geometry("400x350")
    win.configure(bg="#e0e7ef")
    tk.Label(win, text="Your Leave Requests", font=("Segoe UI", 14, "bold"), bg="#e0e7ef", fg="#2563eb").pack(pady=10)
    cur.execute("SELECT reason, status FROM leaves WHERE email=?", (student_email,))
    leaves = cur.fetchall()
    if not leaves:
        tk.Label(win, text="No leave requests submitted.", bg="#e0e7ef", fg="#2563eb").pack(pady=10)
    for idx, (reason, status) in enumerate(leaves):
        tk.Label(win, text=f"{idx+1}. {reason} [{status}]", bg="#e0e7ef", fg="#2563eb", anchor="w").pack(fill="x", padx=10, pady=2)

# === Logout with Confirmation ===
def logout():
    confirm = messagebox.askyesno("Confirm Logout", "Are you sure you want to logout?")
    if confirm:
        root.destroy()

# === Buttons ===
btn_frame = tk.Frame(main_frame, bg="#fff")
btn_frame.pack(pady=20)

tk.Button(btn_frame, text="View Complaints", width=22, height=2, bg="#8e44ad", fg="white", font=("Segoe UI", 11, "bold"), command=view_complaints).pack(pady=7, fill="x")
tk.Button(btn_frame, text="View Leave Requests", width=22, height=2, bg="#3498db", fg="white", font=("Segoe UI", 11, "bold"), command=view_leaves).pack(pady=7, fill="x")
tk.Button(btn_frame, text="Make Complaint", width=22, height=2, bg="#e67e22", fg="white", font=("Segoe UI", 11, "bold"), command=make_complaint).pack(pady=7, fill="x")
tk.Button(btn_frame, text="Request Leave", width=22, height=2, bg="#2ecc71", fg="white", font=("Segoe UI", 11, "bold"), command=request_leave).pack(pady=7, fill="x")
tk.Button(btn_frame, text="View Room", width=22, height=2, bg="#2980b9", fg="white", font=("Segoe UI", 11, "bold"), command=view_room).pack(pady=7, fill="x")
tk.Button(main_frame, text="Logout", width=10, height=1, bg="#c0392b", fg="white", font=("Segoe UI", 11, "bold"), command=logout).pack(pady=20)

root.mainloop()
