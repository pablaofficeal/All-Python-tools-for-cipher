import tkinter as tk
from tkinter import filedialog, messagebox  # Добавлен filedialog
import customtkinter as ctk
import subprocess
import threading
import json
import os

# Конфигурационный файл для сервера
CONFIG_FILE = "server_config.json"

# Загрузка конфигурации
def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return {"port": 5000, "ip": "127.0.0.1", "dns": "example.com"}

# Сохранение конфигурации
def save_config(config):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)

# Класс для управления сервером
class ServerManager:
    def __init__(self):
        self.process = None

    def start_server(self, server_path, config):
        """Запуск сервера с указанной конфигурацией."""
        if self.process is None:
            # Формируем команду для запуска сервера с параметрами
            command = f"{server_path} --port {config['port']} --ip {config['ip']} --dns {config['dns']}"
            self.process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                shell=True
            )
            self.log_output()

    def stop_server(self):
        """Остановка сервера."""
        if self.process:
            self.process.terminate()
            self.process = None

    def log_output(self):
        """Чтение и вывод логов сервера."""
        def read_output():
            while self.process:
                output = self.process.stdout.readline()
                if output:
                    log_text.insert(tk.END, output)
                    log_text.yview(tk.END)
                else:
                    break
        threading.Thread(target=read_output, daemon=True).start()

# Графический интерфейс
class ServerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Управление сервером")
        self.root.geometry("800x600")
        self.server_manager = ServerManager()

        # Загрузка конфигурации
        self.config = load_config()

        # Стиль интерфейса
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Вкладки
        self.tabview = ctk.CTkTabview(root)
        self.tabview.pack(pady=10, padx=10, fill="both", expand=True)

        # Вкладка "Управление сервером"
        self.tabview.add("Управление сервером")
        self.setup_server_tab()

        # Вкладка "Настройки"
        self.tabview.add("Настройки")
        self.setup_settings_tab()

        # Вкладка "Логи"
        self.tabview.add("Логи")
        self.setup_logs_tab()

    def setup_server_tab(self):
        """Вкладка для управления сервером."""
        tab = self.tabview.tab("Управление сервером")

        # Поле для пути к серверу
        self.server_path_label = ctk.CTkLabel(tab, text="Путь к серверу:")
        self.server_path_label.pack(pady=5)

        self.server_path_entry = ctk.CTkEntry(tab, width=400)
        self.server_path_entry.pack(pady=5)

        self.server_path_button = ctk.CTkButton(tab, text="Обзор", command=self.browse_server_path)
        self.server_path_button.pack(pady=5)

        # Кнопки управления сервером
        self.start_button = ctk.CTkButton(tab, text="Старт сервер", command=self.start_server)
        self.start_button.pack(pady=10)

        self.stop_button = ctk.CTkButton(tab, text="Стоп сервер", command=self.stop_server)
        self.stop_button.pack(pady=10)

    def setup_settings_tab(self):
        """Вкладка для настройки сервера."""
        tab = self.tabview.tab("Настройки")

        # Порт
        self.port_label = ctk.CTkLabel(tab, text="Порт:")
        self.port_label.pack(pady=5)

        self.port_entry = ctk.CTkEntry(tab, width=200)
        self.port_entry.pack(pady=5)
        self.port_entry.insert(0, str(self.config["port"]))

        # IP-адрес
        self.ip_label = ctk.CTkLabel(tab, text="IP-адрес:")
        self.ip_label.pack(pady=5)

        self.ip_entry = ctk.CTkEntry(tab, width=200)
        self.ip_entry.pack(pady=5)
        self.ip_entry.insert(0, self.config["ip"])

        # DNS
        self.dns_label = ctk.CTkLabel(tab, text="DNS:")
        self.dns_label.pack(pady=5)

        self.dns_entry = ctk.CTkEntry(tab, width=200)
        self.dns_entry.pack(pady=5)
        self.dns_entry.insert(0, self.config["dns"])

        # Кнопка сохранения настроек
        self.save_button = ctk.CTkButton(tab, text="Сохранить настройки", command=self.save_settings)
        self.save_button.pack(pady=20)

    def setup_logs_tab(self):
        """Вкладка для просмотра логов."""
        tab = self.tabview.tab("Логи")

        global log_text
        log_text = tk.Text(tab, wrap=tk.WORD, bg="#2e2e2e", fg="white", insertbackground="white")
        log_text.pack(pady=10, padx=10, fill="both", expand=True)

    def browse_server_path(self):
        """Выбор пути к серверу."""
        path = filedialog.askopenfilename(filetypes=[("Executable files", "*.exe *.py")])
        if path:
            self.server_path_entry.delete(0, tk.END)
            self.server_path_entry.insert(0, path)

    def start_server(self):
        """Запуск сервера."""
        server_path = self.server_path_entry.get()
        if not server_path:
            messagebox.showerror("Ошибка", "Укажите путь к серверу!")
            return

        # Обновляем конфигурацию
        self.config["port"] = int(self.port_entry.get())
        self.config["ip"] = self.ip_entry.get()
        self.config["dns"] = self.dns_entry.get()
        save_config(self.config)

        # Запускаем сервер
        self.server_manager.start_server(server_path, self.config)

    def stop_server(self):
        """Остановка сервера."""
        self.server_manager.stop_server()

    def save_settings(self):
        """Сохранение настроек."""
        self.config["port"] = int(self.port_entry.get())
        self.config["ip"] = self.ip_entry.get()
        self.config["dns"] = self.dns_entry.get()
        save_config(self.config)
        messagebox.showinfo("Успех", "Настройки сохранены!")

# Запуск приложения
if __name__ == "__main__":
    root = ctk.CTk()
    app = ServerApp(root)
    root.mainloop()