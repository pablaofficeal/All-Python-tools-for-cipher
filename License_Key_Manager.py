import tkinter as tk
from tkinter import ttk, messagebox
import json
import uuid
from cryptography.fernet import Fernet
import base64
import os

class LicenseManager:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Менеджер Лицензионных Ключей")
        self.window.geometry("600x400")
        
        # Генерируем или загружаем ключ для шифрования
        self.key_file = "secret.key"
        self.key = self.load_or_generate_key()
        
        # Создаем интерфейс
        self.create_interface()
        
        # Загружаем существующие ключи
        self.license_keys = self.load_license_keys()

    def load_or_generate_key(self):
        """Загрузка или создание ключа для шифрования"""
        if os.path.exists(self.key_file):
            return open(self.key_file, "rb").read()
        else:
            key = Fernet.generate_key()
            with open(self.key_file, "wb") as key_file:
                key_file.write(key)
            return key

    def generate_license_key(self):
        """Генерация нового лицензионного ключа"""
        raw_uuid = str(uuid.uuid4()).replace('-', '')
        formatted_key = f"{raw_uuid[:5]}-{raw_uuid[5:10]}-{raw_uuid[10:15]}-{raw_uuid[15:20]}-{raw_uuid[20:]}"
        return formatted_key

    def encrypt_data(self, data):
        """Шифрование данных"""
        cipher_suite = Fernet(self.key)
        return cipher_suite.encrypt(data.encode()).decode()

    def decrypt_data(self, encrypted_data):
        """Расшифровка данных"""
        cipher_suite = Fernet(self.key)
        return cipher_suite.decrypt(encrypted_data.encode()).decode()

    def save_license_keys(self):
        """Сохранение ключей в зашифрованном виде"""
        encrypted_data = self.encrypt_data(json.dumps(self.license_keys))
        with open("licenses.dat", "w") as f:
            f.write(encrypted_data)

    def load_license_keys(self):
        """Загрузка сохраненных ключей"""
        if os.path.exists("licenses.dat"):
            try:
                with open("licenses.dat", "r") as f:
                    encrypted_data = f.read()
                    decrypted_data = self.decrypt_data(encrypted_data)
                    return json.loads(decrypted_data)
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось загрузить ключи: {str(e)}")
                return []
        return []

    def create_interface(self):
        """Создание интерфейса"""
        # Фрейм для генерации ключа
        gen_frame = ttk.LabelFrame(self.window, text="Генерация нового ключа", padding=10)
        gen_frame.pack(fill="x", padx=10, pady=5)

        ttk.Button(gen_frame, text="Генерировать ключ", command=self.generate_and_save_key).pack(pady=5)

        # Фрейм для списка ключей
        list_frame = ttk.LabelFrame(self.window, text="Список лицензионных ключей", padding=10)
        list_frame.pack(fill="both", expand=True, padx=10, pady=5)

        columns = ("Ключ", "Дата создания")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings")
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=200)

        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Кнопка удаления ключа
        ttk.Button(self.window, text="Удалить выбранный ключ", command=self.delete_selected_key).pack(pady=5)

    def generate_and_save_key(self):
        """Генерация и сохранение нового ключа"""
        license_key = self.generate_license_key()
        date_created = self.get_current_date()
        
        self.license_keys.append({"key": license_key, "date": date_created})
        self.save_license_keys()
        
        self.update_tree_view()
        messagebox.showinfo("Успех", f"Сгенерирован новый ключ: {license_key}")

    def delete_selected_key(self):
        """Удаление выбранного ключа"""
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Внимание", "Выберите ключ для удаления")
            return
        
        item_index = self.tree.index(selected_item[0])
        del self.license_keys[item_index]
        self.save_license_keys()
        self.update_tree_view()

    def update_tree_view(self):
        """Обновление отображаемого списка ключей"""
        self.tree.delete(*self.tree.get_children())
        for item in self.license_keys:
            self.tree.insert("", "end", values=(item["key"], item["date"]))

    def get_current_date(self):
        """Получение текущей даты"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def run(self):
        """Запуск приложения"""
        self.update_tree_view()
        self.window.mainloop()

if __name__ == "__main__":
    app = LicenseManager()
    app.run()