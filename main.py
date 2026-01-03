import customtkinter as ctk
from tkinter import messagebox
import sqlite3
import os
import webbrowser
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

# --- DIRECTORY SETUP ---
BASE_DIR = "Patient_Data_Vault"
if not os.path.exists(BASE_DIR):
    os.makedirs(BASE_DIR)


# --- DATABASE SETUP ---
def init_db():
    conn = sqlite3.connect("lab_enterprise_v10.db")
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS patients 
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, phone TEXT, 
                       address TEXT, map_link TEXT, notifications INTEGER DEFAULT 1)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS health_records 
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, p_id INTEGER, date TEXT, 
                       test_name TEXT, result_value TEXT)''')
    conn.commit()
    conn.close()


init_db()


class LabProV11(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("EXPERT LAB v11.0 - Easy View Dashboard")
        self.geometry("1350x850")

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- Sidebar ---
        self.sidebar = ctk.CTkFrame(self, width=280, fg_color="#1a1a1a")
        self.sidebar.grid(row=0, column=0, sticky="nsew")

        ctk.CTkLabel(self.sidebar, text="🏥 EXPERT LAB", font=("Helvetica", 28, "bold"), text_color="#3498db").pack(
            pady=40)

        self.nav_btn("📊 Dispatch Dashboard", self.show_dashboard)
        self.nav_btn("👤 New Registration", self.show_reg)
        self.nav_btn("🔍 Search & Add Tests", self.show_search_entry)
        self.nav_btn("📁 Patient Files", lambda: os.startfile(BASE_DIR))

        self.container = ctk.CTkFrame(self, corner_radius=20, fg_color="#121212")
        self.container.grid(row=0, column=1, padx=25, pady=25, sticky="nsew")

        self.show_dashboard()

    def nav_btn(self, text, cmd):
        ctk.CTkButton(self.sidebar, text=text, height=50, command=cmd, fg_color="transparent", border_width=1).pack(
            pady=10, padx=20, fill="x")

    def show_dashboard(self):
        for widget in self.container.winfo_children(): widget.destroy()

        # Dashboard Header
        ctk.CTkLabel(self.container, text="Active Patient Records", font=("Helvetica", 24, "bold"),
                     text_color="white").pack(pady=15)

        # Search Frame
        search_frame = ctk.CTkFrame(self.container, fg_color="transparent")
        search_frame.pack(fill="x", padx=40, pady=10)

        self.dash_search = ctk.CTkEntry(search_frame, placeholder_text="Enter Name or ID to filter...", width=450,
                                        height=45)
        self.dash_search.pack(side="left", padx=10)
        ctk.CTkButton(search_frame, text="🔍 Search", width=120, height=45, command=self.refresh_dashboard).pack(
            side="left")

        # Table Header
        header_frame = ctk.CTkFrame(self.container, fg_color="#222222", height=40)
        header_frame.pack(fill="x", padx=30, pady=(10, 0))
        ctk.CTkLabel(header_frame, text="Patient Details (ID & Name)", font=("Arial", 14, "bold"),
                     text_color="#3498db").pack(side="left", padx=20)
        ctk.CTkLabel(header_frame, text="Quick Actions", font=("Arial", 14, "bold"), text_color="#3498db").pack(
            side="right", padx=100)

        # Scrollable Area
        self.scroll = ctk.CTkScrollableFrame(self.container, fg_color="transparent", width=1000, height=550)
        self.scroll.pack(fill="both", expand=True, padx=20, pady=10)

        self.refresh_dashboard()

    def refresh_dashboard(self):
        for widget in self.scroll.winfo_children(): widget.destroy()
        search_query = self.dash_search.get()

        conn = sqlite3.connect("lab_enterprise_v10.db")
        cur = conn.cursor()
        if search_query:
            cur.execute("SELECT * FROM patients WHERE name LIKE ? OR id=?", (f'%{search_query}%', search_query))
        else:
            cur.execute("SELECT * FROM patients ORDER BY id DESC")

        records = cur.fetchall()

        if not records:
            ctk.CTkLabel(self.scroll, text="No patients found. Please add a new patient.", font=("Arial", 16),
                         text_color="gray").pack(pady=50)

        for p in records:
            card = ctk.CTkFrame(self.scroll, corner_radius=12, fg_color="#1e1e1e", border_width=1,
                                border_color="#333333")
            card.pack(fill="x", pady=6, padx=10)

            # --- Patient Info (Visible Clearly) ---
            info_text = f"ID: {p[0]}   |   Name: {p[1]}"
            ctk.CTkLabel(card, text=info_text, font=("Arial", 18, "bold"), text_color="white").pack(side="left",
                                                                                                    padx=20, pady=20)

            # Action Buttons
            ctk.CTkButton(card, text="🗑️", fg_color="#c0392b", width=40, hover_color="#a93226",
                          command=lambda pid=p[0]: self.delete_patient(pid)).pack(side="right", padx=10)

            notif_text = "Alerts: ON" if p[5] == 1 else "Alerts: OFF"
            notif_color = "#27ae60" if p[5] == 1 else "#7f8c8d"
            ctk.CTkButton(card, text=notif_text, fg_color=notif_color, width=90,
                          command=lambda pid=p[0], s=p[5]: self.toggle_notif(pid, s)).pack(side="right", padx=5)

            ctk.CTkButton(card, text="📍 Rider", fg_color="#e67e22", width=85, font=("Arial", 12, "bold"),
                          command=lambda l=p[4]: webbrowser.open(l)).pack(side="right", padx=5)
            ctk.CTkButton(card, text="📄 PDF", fg_color="#e74c3c", width=70, font=("Arial", 12, "bold"),
                          command=lambda pid=p[0], n=p[1]: self.generate_smart_pdf(pid, n)).pack(side="right", padx=5)
            ctk.CTkButton(card, text="➕ Add Test", fg_color="#3498db", width=95, font=("Arial", 12, "bold"),
                          command=lambda pid=p[0]: self.show_search_entry(pid)).pack(side="right", padx=5)
        conn.close()

    def toggle_notif(self, pid, status):
        new_status = 0 if status == 1 else 1
        conn = sqlite3.connect("lab_enterprise_v10.db")
        cur = conn.cursor()
        cur.execute("UPDATE patients SET notifications = ? WHERE id = ?", (new_status, pid))
        conn.commit()
        conn.close()
        self.refresh_dashboard()

    def delete_patient(self, pid):
        if messagebox.askyesno("Confirm", "Kya aap is mareez ka sara record delete karna chahte hain?"):
            conn = sqlite3.connect("lab_enterprise_v10.db")
            cur = conn.cursor()
            cur.execute("DELETE FROM patients WHERE id = ?", (pid,))
            cur.execute("DELETE FROM health_records WHERE p_id = ?", (pid,))
            conn.commit()
            conn.close()
            self.refresh_dashboard()

    def show_search_entry(self, pre_id=""):
        for widget in self.container.winfo_children(): widget.destroy()
        ctk.CTkLabel(self.container, text="Update Patient Medical Records", font=("Arial", 22, "bold")).pack(pady=20)

        search_f = ctk.CTkFrame(self.container, fg_color="transparent")
        search_f.pack(pady=10)

        self.s_id = ctk.CTkEntry(search_f, placeholder_text="Enter ID...", width=250, height=40)
        self.s_id.insert(0, str(pre_id))
        self.s_id.pack(side="left", padx=10)
        ctk.CTkButton(search_f, text="Load Data", width=120, height=40, command=self.load_patient_for_test).pack(
            side="left")

        self.test_entry_frame = ctk.CTkFrame(self.container, fg_color="transparent")
        self.test_entry_frame.pack(pady=20, fill="both", expand=True)

    def load_patient_for_test(self):
        pid = self.s_id.get()
        conn = sqlite3.connect("lab_enterprise_v10.db")
        cur = conn.cursor()
        cur.execute("SELECT name FROM patients WHERE id=?", (pid,))
        p = cur.fetchone()
        conn.close()

        if p:
            for widget in self.test_entry_frame.winfo_children(): widget.destroy()
            ctk.CTkLabel(self.test_entry_frame, text=f"Updating Record For: {p[0]}", font=("Arial", 18, "bold"),
                         text_color="#2ecc71").pack(pady=15)

            self.test_inputs = []
            for i in range(5):
                f = ctk.CTkFrame(self.test_entry_frame, fg_color="transparent")
                f.pack(pady=3)
                t_name = ctk.CTkEntry(f, placeholder_text="Test Name (e.g. Sugar)", width=250, height=35)
                t_name.pack(side="left", padx=5)
                t_val = ctk.CTkEntry(f, placeholder_text="Result", width=200, height=35)
                t_val.pack(side="left", padx=5)
                self.test_inputs.append((t_name, t_val))

            ctk.CTkButton(self.test_entry_frame, text="✅ Save All Results & Update PDF", fg_color="#2ecc71",
                          hover_color="#27ae60", height=50, width=300, font=("Arial", 14, "bold"),
                          command=self.save_new_tests).pack(pady=30)
        else:
            messagebox.showerror("Error", "Patient ID not found!")

    def save_new_tests(self):
        pid = self.s_id.get()
        date = datetime.now().strftime("%Y-%m-%d")
        conn = sqlite3.connect("lab_enterprise_v10.db")
        cur = conn.cursor()
        for tn, tv in self.test_inputs:
            if tn.get() and tv.get():
                cur.execute("INSERT INTO health_records (p_id, date, test_name, result_value) VALUES (?,?,?,?)",
                            (pid, date, tn.get(), tv.get()))
        conn.commit()
        conn.close()
        messagebox.showinfo("Success", "Medical records updated successfully!")
        self.show_dashboard()

    def generate_smart_pdf(self, p_id, p_name):
        folder = os.path.join(BASE_DIR, p_name.replace(" ", "_"))
        if not os.path.exists(folder): os.makedirs(folder)
        pdf_path = f"{folder}/{p_name}_Report.pdf"

        conn = sqlite3.connect("lab_enterprise_v10.db")
        cur = conn.cursor()
        cur.execute("SELECT name, phone, address FROM patients WHERE id=?", (p_id,))
        p_info = cur.fetchone()
        cur.execute("SELECT date, test_name, result_value FROM health_records WHERE p_id=? ORDER BY date DESC", (p_id,))
        records = cur.fetchall()
        conn.close()

        c = canvas.Canvas(pdf_path, pagesize=A4)
        c.setFont("Helvetica-Bold", 20)
        c.drawCentredString(300, 800, "EXPERT DIAGNOSTIC - HISTORY REPORT")
        c.setFont("Helvetica", 11)
        c.drawString(50, 760, f"Patient: {p_info[0]}  |  ID: {p_id}")
        c.drawString(50, 745, f"Contact: {p_info[1]}  |  Address: {p_info[2]}")
        c.line(50, 735, 550, 735)

        y = 710
        c.setFont("Helvetica-Bold", 11)
        c.drawString(50, y, "DATE");
        c.drawString(180, y, "TEST DESCRIPTION");
        c.drawString(450, y, "RESULT")
        y -= 25
        c.setFont("Helvetica", 10)
        for r in records:
            c.drawString(50, y, str(r[0]));
            c.drawString(180, y, str(r[1]));
            c.drawString(450, y, str(r[2]))
            y -= 20
            if y < 80: c.showPage(); y = 800
        c.save()
        os.startfile(pdf_path)

    def show_reg(self):
        for widget in self.container.winfo_children(): widget.destroy()
        ctk.CTkLabel(self.container, text="New Patient Registration", font=("Arial", 24, "bold")).pack(pady=30)
        self.e_name = ctk.CTkEntry(self.container, placeholder_text="Full Name", width=450, height=45);
        self.e_name.pack(pady=10)
        self.e_ph = ctk.CTkEntry(self.container, placeholder_text="Phone Number", width=450, height=45);
        self.e_ph.pack(pady=10)
        self.e_adr = ctk.CTkEntry(self.container, placeholder_text="Address", width=450, height=45);
        self.e_adr.pack(pady=10)
        self.e_map = ctk.CTkEntry(self.container, placeholder_text="Google Maps Link", width=450, height=45);
        self.e_map.pack(pady=10)
        ctk.CTkButton(self.container, text="Register Patient", fg_color="#3498db", font=("Arial", 16, "bold"),
                      height=55, width=250, command=self.save_p).pack(pady=30)

    def save_p(self):
        conn = sqlite3.connect("lab_enterprise_v10.db")
        cur = conn.cursor()
        cur.execute("INSERT INTO patients (name, phone, address, map_link) VALUES (?,?,?,?)",
                    (self.e_name.get(), self.e_ph.get(), self.e_adr.get(), self.e_map.get()))
        conn.commit()
        conn.close()
        messagebox.showinfo("Success", "Patient Profile Created!")
        self.show_dashboard()


if __name__ == "__main__":
    app = LabProV11()
    app.mainloop()