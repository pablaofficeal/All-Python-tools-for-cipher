import tkinter as tk
from tkinter import messagebox, filedialog, simpledialog
from cryptography.fernet import Fernet
import pyperclip
import json
import os
import platform

# Определяем путь к системной папке
if platform.system() == "Windows":
    BASE_DIR = os.path.join(os.getenv('APPDATA'), "CipherApp")
else:
    BASE_DIR = "/var/lib/CipherApp"

# Создаем папку, если она не существует
os.makedirs(BASE_DIR, exist_ok=True)

# Пути к файлам
HISTORY_FILE = os.path.join(BASE_DIR, "history.json")
LICENSE_FILE = os.path.join(BASE_DIR, "license.json")

# Класс для шифрования и дешифрования
class CustomCipher:
    def __init__(self):
        # Задаем алфавиты и шифрованные данные
        self.russian_alphabet = ['а', 'б', 'в', 'г', 'д', 'е', 'ё', 'ж', 'з', 'и', 'й', 'к', 'л', 'м', 'н', 'о', 'п', 'р', 'с', 'т', 'у', 'ф', 'х', 'ц', 'ч', 'ш', 'щ', 'ъ', 'ы', 'ь', 'э', 'ю', 'я']
        self.encrypted_alphabet = ['м', 'а', 'г', 'б', 'в', 'ж', 'з', 'е', 'х', 'у', 'к', 'и', 'ы', 'э', 'ё', 'ъ', 'о', 'п', 'р', 'с', 'т', 'я', 'ю', 'д', 'ц', 'ч', 'ш', 'щ', 'л', 'н', 'ф', 'ь', 'й']
        self.digits = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0']
        self.encrypted_digits = ['5', '0', '7', '8', '6', '1', '2', '4', '3', '9']

        # Создаем словари для шифрования и дешифрования
        self.encrypt_dict = {original: encrypted for original, encrypted in zip(self.russian_alphabet, self.encrypted_alphabet)}
        self.decrypt_dict = {encrypted: original for original, encrypted in zip(self.russian_alphabet, self.encrypted_alphabet)}
        self.encrypt_digit_dict = {original: encrypted for original, encrypted in zip(self.digits, self.encrypted_digits)}
        self.decrypt_digit_dict = {encrypted: original for original, encrypted in zip(self.digits, self.encrypted_digits)}

        # Генерация ключа для дополнительного шифрования
        self.key = Fernet.generate_key()
        self.cipher = Fernet(self.key)

    def encrypt_text(self, text):
        # Шифруем текст с использованием кастомного шифра
        encrypted_text = []
        for char in text:
            if char.lower() in self.encrypt_dict:
                encrypted_text.append(self.encrypt_dict[char.lower()])
            elif char in self.encrypt_digit_dict:
                encrypted_text.append(self.encrypt_digit_dict[char])
            else:
                encrypted_text.append(char)  # Оставляем символ как есть, если он не в алфавите
        encrypted_text = ''.join(encrypted_text)

        # Дополнительное шифрование с использованием cryptography
        encrypted_text = self.cipher.encrypt(encrypted_text.encode()).decode()
        return encrypted_text

    def decrypt_text(self, encrypted_text):
        # Расшифровываем текст с использованием cryptography
        try:
            decrypted_text = self.cipher.decrypt(encrypted_text.encode()).decode()
        except:
            return "Ошибка: Неверный формат зашифрованного текста!"

        # Расшифровываем текст с использованием кастомного шифра
        result = []
        for char in decrypted_text:
            if char.lower() in self.decrypt_dict:
                result.append(self.decrypt_dict[char.lower()])
            elif char in self.decrypt_digit_dict:
                result.append(self.decrypt_digit_dict[char])
            else:
                result.append(char)  # Оставляем символ как есть, если он не в алфавите
        return ''.join(result)

# Графический интерфейс
class CipherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Приложение для шифрования и дешифрования")
        self.cipher = CustomCipher()

        # Загрузка лицензии
        self.load_license()

        # Поле ввода текста
        self.input_label = tk.Label(root, text="Введите текст:")
        self.input_label.pack()
        self.input_text = tk.Text(root, height=5, width=50)
        self.input_text.pack()

        # Кнопки для шифрования и дешифрования
        self.encrypt_button = tk.Button(root, text="Зашифровать", command=self.encrypt)
        self.encrypt_button.pack()
        self.decrypt_button = tk.Button(root, text="Расшифровать", command=self.decrypt)
        self.decrypt_button.pack()

        # Поле вывода результата
        self.output_label = tk.Label(root, text="Результат:")
        self.output_label.pack()
        self.output_text = tk.Text(root, height=5, width=50, state='disabled')
        self.output_text.pack()

        # Кнопка для копирования результата
        self.copy_button = tk.Button(root, text="Копировать результат", command=self.copy_result)
        self.copy_button.pack()

        # Кнопка для сохранения результата в файл
        self.save_button = tk.Button(root, text="Сохранить результат", command=self.save_result)
        self.save_button.pack()

        # Кнопка для просмотра истории
        self.history_button = tk.Button(root, text="Просмотреть историю", command=self.view_history)
        self.history_button.pack()

        # Кнопка для очистки истории
        self.clear_history_button = tk.Button(root, text="Очистить историю", command=self.clear_history)
        self.clear_history_button.pack()

    def load_license(self):
        # Загрузка лицензии из файла
        if os.path.exists(LICENSE_FILE):
            with open(LICENSE_FILE, "r", encoding="utf-8") as file:
                self.license_data = json.load(file)
        else:
            self.license_data = {"license_key": "DEMO", "expiry_date": "2025-12-31"}
            with open(LICENSE_FILE, "w", encoding="utf-8") as file:
                json.dump(self.license_data, file)

    def save_history(self, operation, text, result):
        # Сохранение операции в историю
        history_entry = {
            "operation": operation,
            "input_text": text,
            "output_text": result,
            "timestamp": tk.simpledialog.askstring("История", "Добавьте комментарий к операции:")
        }
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, "r", encoding="utf-8") as file:
                history = json.load(file)
        else:
            history = []
        history.append(history_entry)
        with open(HISTORY_FILE, "w", encoding="utf-8") as file:
            json.dump(history, file, ensure_ascii=False, indent=4)

    def view_history(self):
        # Просмотр истории
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, "r", encoding="utf-8") as file:
                history = json.load(file)
            history_text = "\n".join([f"{entry['operation']}: {entry['input_text']} -> {entry['output_text']} ({entry['timestamp']})" for entry in history])
            messagebox.showinfo("История операций", history_text)
        else:
            messagebox.showinfo("История операций", "История пуста.")

    def clear_history(self):
        # Очистка истории
        if os.path.exists(HISTORY_FILE):
            os.remove(HISTORY_FILE)
            messagebox.showinfo("Успех", "История очищена!")
        else:
            messagebox.showinfo("История операций", "История уже пуста.")

    def encrypt(self):
        text = self.input_text.get("1.0", tk.END).strip()
        if text:
            encrypted_text = self.cipher.encrypt_text(text)
            self.output_text.config(state='normal')
            self.output_text.delete("1.0", tk.END)
            self.output_text.insert(tk.END, encrypted_text)
            self.output_text.config(state='disabled')
            self.save_history("Шифрование", text, encrypted_text)
        else:
            messagebox.showwarning("Ошибка", "Введите текст для шифрования!")

    def decrypt(self):
        text = self.input_text.get("1.0", tk.END).strip()
        if text:
            decrypted_text = self.cipher.decrypt_text(text)
            # Улучшаем читаемость текста (добавляем пробелы между словами)
            decrypted_text = self.improve_readability(decrypted_text)
            self.output_text.config(state='normal')
            self.output_text.delete("1.0", tk.END)
            self.output_text.insert(tk.END, decrypted_text)
            self.output_text.config(state='disabled')
            self.save_history("Дешифрование", text, decrypted_text)
        else:
            messagebox.showwarning("Ошибка", "Введите текст для дешифрования!")

    def improve_readability(self, text):
        # Добавляем пробелы между словами для улучшения читаемости
        return " ".join(text.split())

    def copy_result(self):
        result = self.output_text.get("1.0", tk.END).strip()
        if result:
            pyperclip.copy(result)
            messagebox.showinfo("Успех", "Результат скопирован в буфер обмена!")
        else:
            messagebox.showwarning("Ошибка", "Нет результата для копирования!")

    def save_result(self):
        result = self.output_text.get("1.0", tk.END).strip()
        if result:
            file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Текстовые файлы", "*.txt")])
            if file_path:
                with open(file_path, "w", encoding="utf-8") as file:
                    file.write(result)
                messagebox.showinfo("Успех", f"Результат сохранен в файл: {file_path}")
        else:
            messagebox.showwarning("Ошибка", "Нет результата для сохранения!")

# Запуск приложения
if __name__ == "__main__":
    root = tk.Tk()
    app = CipherApp(root)
    root.mainloop()