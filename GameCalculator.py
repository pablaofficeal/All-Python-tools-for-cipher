import tkinter as tk
from tkinter import ttk, messagebox
import json
import sqlite3
from cryptography.fernet import Fernet
import base64
import os
from datetime import datetime

class EncryptionManager:
    def __init__(self):
        self.key = self._load_or_create_key()
        self.cipher_suite = Fernet(self.key)
    
    def _load_or_create_key(self):
        if os.path.exists('secret.key'):
            with open('secret.key', 'rb') as key_file:
                return key_file.read()
        else:
            key = Fernet.generate_key()
            with open('secret.key', 'wb') as key_file:
                key_file.write(key)
            return key
    
    def encrypt_data(self, data):
        return self.cipher_suite.encrypt(json.dumps(data).encode())
    
    def decrypt_data(self, encrypted_data):
        return json.loads(self.cipher_suite.decrypt(encrypted_data))

class GameCalculator:
    def __init__(self):
        # Инициализация основных компонентов
        self.root = tk.Tk()
        self.root.title("Игровой Калькулятор")
        
        # Переменные для отслеживания прогресса
        self.points = tk.IntVar(value=0)
        self.tokens = tk.IntVar(value=0)
        self.current_skin = tk.StringVar(value="classic")
        
        # Настройка скинов и их стоимости
        self.skins = {
            "classic": {"color": "#F0F0F0"},
            "dark": {"color": "#2b2b2b", "cost": 100},
            "neon": {"color": "#000033", "cost": 200}
        }
        
        # Инициализация шифрования и базы данных
        self.encryption_manager = EncryptionManager()
        self.init_database()
        
        # Загрузка сохраненного прогресса
        self.load_progress()
        
        self.setup_ui()
    
    def init_database(self):
        """Инициализация SQLite базы данных"""
        self.conn = sqlite3.connect('calculator.db')
        self.cursor = self.conn.cursor()
        
        # Создание таблицы истории
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY,
            expression TEXT,
            result TEXT,
            timestamp DATETIME,
            points_gained INTEGER
        )''')
        
        # Создание таблицы настроек
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            setting_name TEXT PRIMARY KEY,
            value TEXT
        )''')
        
        self.conn.commit()
    
    def setup_ui(self):
        """Настройка интерфейса"""
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Поле ввода
        self.expression = tk.StringVar()
        self.entry_field = ttk.Entry(main_frame, textvariable=self.expression, width=35)
        self.entry_field.grid(row=0, column=0, columnspan=4, pady=5)
        
        # Кнопки калькулятора
        buttons = [
            '7', '8', '9', '/',
            '4', '5', '6', '*',
            '1', '2', '3', '-',
            '0', '.', '=', '+'
        ]
        
        row_val = 1
        col_val = 0
        
        for button in buttons:
            cmd = lambda x=button: self.click(x)
            ttk.Button(main_frame, text=button, command=cmd).grid(
                row=row_val, column=col_val, padx=5, pady=5
            )
            
            col_val += 1
            if col_val > 3:
                col_val = 0
                row_val += 1
        
        # Панель статистики
        stats_frame = ttk.LabelFrame(main_frame, text="Статистика", padding="5")
        stats_frame.grid(row=row_val+1, column=0, columnspan=4, pady=10, sticky=(tk.W, tk.E))
        
        self.points_label = ttk.Label(stats_frame, text=f"Очки: {self.points.get()}")
        self.points_label.grid(row=0, column=0)
        self.tokens_label = ttk.Label(stats_frame, text=f"Токены: {self.tokens.get()}")
        self.tokens_label.grid(row=0, column=1)
        
        # Кнопка магазина
        ttk.Button(
            main_frame,
            text="Магазин",
            command=self.open_shop
        ).grid(row=row_val+2, column=0, columnspan=4, pady=10)
    
    def click(self, key):
        if key == '=':
            try:
                result = str(eval(self.expression.get()))
                self.save_to_history(self.expression.get(), result)
                self.update_points(len(self.expression.get()))
                self.expression.set(result)
            except Exception as e:
                self.expression.set("Ошибка")
                print(f"Error: {e}")
        else:
            self.expression.set(self.expression.get() + str(key))
    
    def save_to_history(self, expression, result):
        """Сохранение вычисления в зашифрованную историю"""
        timestamp = datetime.now().isoformat()
        
        # Шифруем данные
        encrypted_data = self.encryption_manager.encrypt_data({
            'expression': expression,
            'result': result,
            'timestamp': timestamp
        })
        
        # Сохраняем в базу данных
        self.cursor.execute('''
        INSERT INTO history (expression, result, timestamp, points_gained)
        VALUES (?, ?, ?, ?)
        ''', (encrypted_data, result, timestamp, len(expression)))
        self.conn.commit()
    
    def update_points(self, calculation_length):
        """Обновление системы очков с учетом длины выражения"""
        base_points = min(calculation_length * 2, 100)  # Максимально 100 очков
        
        # Бонусные очки за сложность расчета
        complexity_bonus = {
            range(1, 6): 0,
            range(6, 11): 25,
            range(11, 16): 50,
            range(16, float('inf')): 100
        }
        
        bonus = next(bonus for r, bonus in complexity_bonus.items() 
                    if calculation_length in r)
        
        total_points = base_points + bonus
        
        # Удвоение очков при наличии токенов
        if self.tokens.get() > 0:
            total_points *= 2
            
        self.points.set(self.points.get() + total_points)
        
        # Обновляем метки статистики
        self.points_label.config(text=f"Очки: {self.points.get()}")
        self.tokens_label.config(text=f"Токены: {self.tokens.get()}")
        
        # Сохраняем прогресс
        self.save_progress()
    
    def load_progress(self):
        """Загрузка сохраненного прогресса"""
        try:
            with open("calculator_save.json", "r") as f:
                progress = json.load(f)
                self.points.set(progress["points"])
                self.tokens.set(progress["tokens"])
                self.current_skin.set(progress["skin"])
                self.apply_current_skin()
        except FileNotFoundError:
            pass
    
    def save_progress(self):
        """Сохранение прогресса"""
        progress = {
            "points": self.points.get(),
            "tokens": self.tokens.get(),
            "skin": self.current_skin.get()
        }
        with open("calculator_save.json", "w") as f:
            json.dump(progress, f)
    
    def open_shop(self):
        """Открытие магазина скинов"""
        shop_window = tk.Toplevel(self.root)
        shop_window.title("Магазин скинов")
        shop_window.geometry("300x400")
        
        # Заголовок
        ttk.Label(shop_window, text="Доступные скины", font=('Arial', 14)).pack(pady=10)
        
        # Список доступных скинов
        for skin_name, skin_data in self.skins.items():
            frame = ttk.Frame(shop_window)
            frame.pack(fill=tk.X, padx=10, pady=5)
            
            # Информация о скине
            info_text = f"{skin_name.capitalize()}"
            if 'cost' in skin_data:
                info_text += f" - {skin_data['cost']} очков"
            ttk.Label(frame, text=info_text).pack(side=tk.LEFT)
            
            # Кнопка покупки
            if 'cost' in skin_data:
                cmd = lambda s=skin_name, c=skin_data['cost']: self.buy_skin(s, c)
                ttk.Button(
                    frame,
                    text="Купить",
                    command=cmd
                ).pack(side=tk.RIGHT)
    
    def buy_skin(self, skin_name, cost):
        """Покупка скина"""
        if self.points.get() >= cost:
            # Вычитаем очки
            self.points.set(self.points.get() - cost)
            
            # Применяем новый скин
            self.current_skin.set(skin_name)
            self.apply_current_skin()
            
            # Обновляем метки статистики
            self.points_label.config(text=f"Очки: {self.points.get()}")
            
            # Сохраняем изменения
            self.save_progress()
            
            messagebox.showinfo(
                "Успех!",
                f"Скин '{skin_name}' успешно применён!"
            )
        else:
            messagebox.showerror(
                "Ошибка",
                "Недостаточно очков для покупки этого скина!"
            )
    
    def apply_current_skin(self):
        """Применение текущего скина"""
        current_color = self.skins[self.current_skin.get()]["color"]
        
        # Меняем цвет фона основного окна
        self.root.configure(bg=current_color)
        
        # Меняем цвет фона всех виджетов
        for widget in self.root.winfo_children():
            widget.configure(bg=current_color)
    
    def run(self):
        """Запуск калькулятора"""
        self.root.mainloop()

if __name__ == "__main__":
    app = GameCalculator()
    app.run()
