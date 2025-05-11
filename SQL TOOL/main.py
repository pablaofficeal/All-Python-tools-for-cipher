import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import sqlite3
import json
import os
import time
import threading
import random
import math
import psutil

# Настройки приложения
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class AwesomeDBApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Ultra Database Master 9000")
        self.geometry("1400x800")
        self.iconbitmap("database.ico")
        self.configure(fg_color=("#1E1E1E", "#1E1E1E"))
        
        # Переменные
        self.db_conn = None
        self.current_data = None
        self.history = []
        self.history_index = -1
        self.animations_running = True
        
        # Создание интерфейса
        self.create_ui()
        
        # Запуск анимаций
        self.start_background_animations()
        
    def create_ui(self):
        # Главный контейнер
        self.main_container = ctk.CTkFrame(self, corner_radius=0)
        self.main_container.pack(fill="both", expand=True)
        
        # Левая панель (Сайдбар)
        self.create_sidebar()
        
        # Основная область
        self.main_area = ctk.CTkFrame(self.main_container, corner_radius=0)
        self.main_area.pack(side="right", fill="both", expand=True)
        
        # Вкладки
        self.notebook = ttk.Notebook(self.main_area)
        self.notebook.pack(fill="both", expand=True)
        
        # Таблица данных
        self.create_data_tab()
        
        # Терминал
        self.create_terminal_tab()
        
        # Статус бар
        self.create_status_bar()
        
    def create_sidebar(self):
        self.sidebar = ctk.CTkFrame(self.main_container, width=300, corner_radius=0)
        self.sidebar.pack(side="left", fill="y")
        
        # Анимированный логотип
        self.logo_canvas = tk.Canvas(self.sidebar, width=250, height=250, bg="#1E1E1E", highlightthickness=0)
        self.logo_canvas.pack(pady=40)
        self.draw_logo_animation()
        
        # Кнопки
        self.btn_open = ctk.CTkButton(
            self.sidebar,
            text="📂 Open File",
            command=self.open_file,
            fg_color="transparent",
            border_width=2,
            hover_color=("#2B2B2B", "#1E1E1E"),
            font=("Arial", 14, "bold")
        )
        self.btn_open.pack(pady=10, fill="x", padx=20)
        
        # Анимация частиц
        self.particle_canvas = tk.Canvas(self.sidebar, width=280, height=200, bg="#1E1E1E", highlightthickness=0)
        self.particle_canvas.pack(pady=20)
        self.particles = []
        
        # Прогресс бар
        self.progress = ctk.CTkProgressBar(self.sidebar, orientation="horizontal", height=20)
        self.progress.pack(pady=20, fill="x", padx=20)
        self.progress.set(0)
        
    def draw_logo_animation(self):
        self.logo_canvas.delete("all")
        colors = ["#FF0000", "#00FF00", "#0000FF", "#FF00FF"]
        for i in range(8):
            angle = math.radians(45 * i)
            x1 = 125 + 80 * math.cos(angle)
            y1 = 125 + 80 * math.sin(angle)
            x2 = 125 + 100 * math.cos(angle)
            y2 = 125 + 100 * math.sin(angle)
            self.logo_canvas.create_line(
                x1, y1, x2, y2,
                width=5,
                fill=random.choice(colors),
                tags="logo"
            )
        if self.animations_running:
            self.after(100, self.rotate_logo)
            
    def rotate_logo(self):
        self.logo_canvas.delete("logo")
        self.logo_canvas.create_arc(
            50, 50, 200, 200,
            start=0,
            extent=359,
            style="arc",
            outline="#00FF88",
            width=5
        )
        self.draw_logo_animation()
        
    def create_data_tab(self):
        self.data_tab = ctk.CTkFrame(self.notebook)
        self.notebook.add(self.data_tab, text="📊 Data")
        
        # Хедер таблицы
        self.table_header = ctk.CTkFrame(self.data_tab, height=40)
        self.table_header.pack(fill="x")
        
        # Таблица
        self.tree = ttk.Treeview(
            self.data_tab,
            style="Treeview",
            selectmode="extended",
            columns=[],
            show="headings"
        )
        self.tree.pack(fill="both", expand=True)
        
        # Скроллбары
        vsb = ttk.Scrollbar(self.data_tab, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(self.data_tab, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        vsb.pack(side="right", fill="y")
        hsb.pack(side="bottom", fill="x")
        
    def create_terminal_tab(self):
        self.terminal_tab = ctk.CTkFrame(self.notebook)
        self.notebook.add(self.terminal_tab, text="💻 Terminal")
        
        # Вывод терминала
        self.term_output = ctk.CTkTextbox(
            self.terminal_tab,
            wrap="word",
            font=("Consolas", 12),
            fg_color="black"
        )
        self.term_output.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Ввод команд
        self.cmd_entry = ctk.CTkEntry(
            self.terminal_tab,
            height=30,
            font=("Consolas", 12)
        )
        self.cmd_entry.pack(fill="x", padx=5, pady=5)
        self.cmd_entry.bind("<Return>", self.execute_command)
        
    def create_status_bar(self):
        self.status_bar = ctk.CTkFrame(self, height=30, corner_radius=0)
        self.status_bar.pack(side="bottom", fill="x")
        
        self.status_label = ctk.CTkLabel(
            self.status_bar,
            text="🚀 Ready",
            anchor="w",
            font=("Arial", 12)
        )
        self.status_label.pack(side="left", padx=10)
        
        self.memory_usage = ctk.CTkLabel(
            self.status_bar,
            text="💾 Memory: 0 MB",
            anchor="e",
            font=("Arial", 12)
        )
        self.memory_usage.pack(side="right", padx=10)
        
    def start_background_animations(self):
        threading.Thread(target=self.particle_animation, daemon=True).start()
        threading.Thread(target=self.update_memory_usage, daemon=True).start()
        
    def particle_animation(self):
        colors = ["#FF0000", "#00FF00", "#0000FF", "#FF00FF", "#FFFF00"]
        while self.animations_running:
            if len(self.particles) < 100:
                x = random.randint(0, 280)
                y = random.randint(0, 200)
                size = random.randint(2, 5)
                color = random.choice(colors)
                particle = self.particle_canvas.create_oval(
                    x, y, x+size, y+size,
                    fill=color,
                    outline=color
                )
                self.particles.append(particle)
                
            for particle in self.particles:
                self.particle_canvas.move(particle, 0, 1)
                pos = self.particle_canvas.coords(particle)
                if pos[1] > 200:
                    self.particle_canvas.delete(particle)
                    self.particles.remove(particle)
                    
            time.sleep(0.01)
            
    def update_memory_usage(self):
        while self.animations_running:
            memory = round(psutil.Process(os.getpid()).memory_info().rss / (1024 * 1024), 2)
            self.memory_usage.configure(text=f"💾 Memory: {memory} MB")
            time.sleep(1)
            
    def open_file(self):
        filetypes = [
            ("Database files", "*.db *.sqlite"),
            ("JSON files", "*.json")
        ]
        filepath = filedialog.askopenfilename(filetypes=filetypes)
        if filepath:
            self.start_loading_animation()
            threading.Thread(target=self.load_file, args=(filepath,), daemon=True).start()
            
    def start_loading_animation(self):
        self.progress.configure(progress_color="#00FF88")
        for i in range(101):
            self.progress.set(i/100)
            self.update()
            time.sleep(0.01)
            
    def load_file(self, filepath):
        try:
            if filepath.endswith(".json"):
                with open(filepath, "r") as f:
                    self.current_data = json.load(f)
                self.display_json_data()
            elif filepath.endswith((".db", ".sqlite")):
                self.db_conn = sqlite3.connect(filepath)
                self.display_db_tables()
        except Exception as e:
            self.show_error(f"Error loading file: {str(e)}")
        finally:
            self.stop_loading_animation()
            
    def stop_loading_animation(self):
        self.progress.set(1)
        self.after(500, lambda: self.progress.set(0))
        
    def execute_command(self, event=None):
        command = self.cmd_entry.get()
        if command.strip() == "":
            return
        
        self.cmd_entry.delete(0, "end")
        self.term_output.configure(state="normal")
        self.term_output.insert("end", f">>> {command}\n")
        
        try:
            if self.db_conn:
                cursor = self.db_conn.cursor()
                cursor.execute(command)
                if command.strip().lower().startswith("select"):
                    result = cursor.fetchall()
                    self.term_output.insert("end", f"{result}\n")
                else:
                    self.db_conn.commit()
                    self.term_output.insert("end", "Command executed successfully.\n")
        except Exception as e:
            self.term_output.insert("end", f"Error: {str(e)}\n")
        
        self.term_output.configure(state="disabled")
        self.term_output.see("end")
        
    def display_json_data(self):
        if isinstance(self.current_data, list) and len(self.current_data) > 0:
            headers = list(self.current_data[0].keys())
            self.tree["columns"] = headers
            for header in headers:
                self.tree.heading(header, text=header)
                self.tree.column(header, width=100, anchor="w")
                
            for item in self.current_data:
                self.tree.insert("", "end", values=[item.get(header, "") for header in headers])
                
    def display_db_tables(self):
        if self.db_conn:
            cursor = self.db_conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            if tables:
                self.current_table = tables[0][0]
                self.display_table_data(self.current_table)
                
    def display_table_data(self, table_name):
        if self.db_conn:
            cursor = self.db_conn.cursor()
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            self.tree["columns"] = [col[1] for col in columns]
            for col in columns:
                self.tree.heading(col[1], text=col[1])
                self.tree.column(col[1], width=100, anchor="w")
                
            cursor.execute(f"SELECT * FROM {table_name}")
            for row in cursor.fetchall():
                self.tree.insert("", "end", values=row)
                
    def show_error(self, message):
        messagebox.showerror("Error", message)
        
    def __del__(self):
        self.animations_running = False
        if self.db_conn:
            self.db_conn.close()

if __name__ == "__main__":
    app = AwesomeDBApp()
    app.mainloop()