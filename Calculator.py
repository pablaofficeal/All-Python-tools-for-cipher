import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import json
import base64
from cryptography.fernet import Fernet
import os

class Calculator:
    def __init__(self, master):
        self.master = master
        self.history = []
        
        # Generate encryption key on first run
        self.key_path = "main.key"
        self.history_path = "calculator_history.dat"
        self.key = self._generate_or_load_key()
        
        # Load history on startup
        self.history = self.load_history()
        
        # Style configuration
        self.style = ttk.Style()
        self.style.configure('TButton', font=('Arial', 12))
        self.style.configure('TEntry', font=('Arial', 16))
        
        # Main frame
        self.main_frame = ttk.Frame(master, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Entry field
        self.entry = ttk.Entry(self.main_frame, justify='right')
        self.entry.grid(row=0, column=0, columnspan=4, pady=5, sticky=(tk.W, tk.E))
        
        # Calculator buttons (vertical layout)
        buttons = [
            ['7', '8', '9', '/'],
            ['4', '5', '6', '*'],
            ['1', '2', '3', '-'],
            ['0', '.', '=', '+'],
            ['Очистить']
        ]
        
        row_val = 1
        col_val = 0
        
        for row in buttons:
            for button in row:
                cmd = lambda x=button: self.click(x)
                ttk.Button(self.main_frame, text=button, command=cmd).grid(
                    row=row_val, column=col_val, padx=2, pady=2, sticky=(tk.W, tk.E))
                col_val += 1
            row_val += 1
            col_val = 0
        
        # History button
        ttk.Button(self.main_frame, text="История", command=self.show_history).grid(
            row=row_val, column=0, columnspan=4, pady=5, sticky=(tk.W, tk.E))
        
        # Configure expandability
        master.columnconfigure(0, weight=1)
        master.rowconfigure(0, weight=1)
        for i in range(4):
            self.main_frame.columnconfigure(i, weight=1)

    def _generate_or_load_key(self):
        """Generate or load encryption key"""
        if os.path.exists(self.key_path):
            with open(self.key_path, 'rb') as key_file:
                return key_file.read()
        else:
            key = Fernet.generate_key()
            with open(self.key_path, 'wb') as key_file:
                key_file.write(key)
            return key

    def _encrypt_data(self, data):
        """Encrypt data"""
        f = Fernet(self.key)
        return base64.b64encode(f.encrypt(json.dumps(data).encode())).decode()

    def _decrypt_data(self, encrypted_data):
        """Decrypt data"""
        f = Fernet(self.key)
        return json.loads(f.decrypt(base64.b64decode(encrypted_data)).decode())

    def save_history(self):
        """Save history to encrypted file"""
        encrypted_history = self._encrypt_data(self.history)
        with open(self.history_path, 'w') as history_file:
            history_file.write(encrypted_history)

    def load_history(self):
        """Load history from encrypted file"""
        if not os.path.exists(self.history_path):
            return []
        
        try:
            with open(self.history_path, 'r') as history_file:
                encrypted_data = history_file.read()
                return self._decrypt_data(encrypted_data)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить историю: {str(e)}")
            return []

    def click(self, value):
        if value == '=':
            try:
                result = str(eval(self.entry.get()))
                calculation = f"{self.entry.get()} = {result}"
                self.history.append({
                    'time': datetime.now().strftime("%H:%M:%S"),
                    'calculation': calculation
                })
                self.save_history()  # Save history after each calculation
                self.entry.delete(0, tk.END)
                self.entry.insert(tk.END, result)
            except ZeroDivisionError:
                messagebox.showerror("Ошибка", "Деление на ноль невозможно")
                self.clear()
            except Exception:
                messagebox.showerror("Ошибка", "Неверное выражение")
                self.clear()
        elif value == 'Очистить':
            self.clear()
        else:
            self.entry.insert(tk.END, value)

    def clear(self):
        """Clear the entry field"""
        self.entry.delete(0, tk.END)

    def show_history(self):
        """Show calculation history in a new window"""
        history_window = tk.Toplevel(self.master)
        history_window.title("История вычислений")
        history_window.geometry("400x500")
        
        # History list with scrollbar
        frame = ttk.Frame(history_window)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        scrollbar = ttk.Scrollbar(frame, orient='vertical')
        history_list = tk.Listbox(frame, width=50, height=20, yscrollcommand=scrollbar.set)
        scrollbar.config(command=history_list.yview)
        
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        history_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Populate history list
        for item in self.history:
            history_list.insert(tk.END, f"[{item['time']}] {item['calculation']}")
        
        # History control buttons
        ttk.Button(history_window, text="Очистить историю",
                  command=lambda: self.clear_history(history_list)).pack(pady=5)
        ttk.Button(history_window, text="Экспорт в файл",
                  command=self.export_history).pack(pady=5)

    def clear_history(self, history_list):
        """Clear the history"""
        self.history = []
        self.save_history()
        history_list.delete(0, tk.END)

    def export_history(self):
        """Export history to a text file"""
        try:
            with open("calculator_export.txt", "w", encoding="utf-8") as export_file:
                export_file.write("История вычислений:\n\n")
                for item in self.history:
                    export_file.write(f"[{item['time']}] {item['calculation']}\n")
            messagebox.showinfo("Успех", "История успешно экспортирована в calculator_export.txt")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось экспортировать историю: {str(e)}")

# Main application
root = tk.Tk()
root.title("Расширенный калькулятор")
calc = Calculator(root)
root.mainloop()
