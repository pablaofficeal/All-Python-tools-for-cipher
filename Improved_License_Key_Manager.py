import tkinter as tk
from tkinter import ttk, messagebox
import json
import uuid
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
import base64
import os
import hashlib
import zlib
import pyperclip
from datetime import datetime

class LicenseManager:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Улучшенный Менеджер Лицензионных Ключей")
        self.window.geometry("650x450")
        
        # Загрузка настроек темы
        self.theme = self.load_theme_settings()
        self.window.configure(bg=self.theme["background"])
        
        # Генерируем или загружаем ключи для шифрования
        self.key_files = {
            "secret.key": "secret.key",
            "salt.dat": "salt.dat",
            "rsa_private.pem": "rsa_private.pem",
            "rsa_public.pem": "rsa_public.pem"
        }
        
        self.keys = self.load_or_generate_keys()
        self.create_interface()
        self.license_keys = self.load_license_keys()

    def load_theme_settings(self):
        """Загрузка настроек темы"""
        themes = {
            "light": {
                "background": "#ffffff",
                "text": "#000000",
                "button": "#e0e0e0",
                "frame": "#f0f0f0",
                "highlight": "#007bff"
            },
            "dark": {
                "background": "#2b2b2b",
                "text": "#ffffff",
                "button": "#404040",
                "frame": "#3b3b3b",
                "highlight": "#00ff00"
            }
        }
        
        if os.path.exists("theme.dat"):
            try:
                with open("theme.dat", "r") as f:
                    return themes.get(json.load(f)["theme"], themes["light"])
            except:
                return themes["light"]
        return themes["light"]

    def save_theme_settings(self, theme_name):
        """Сохранение настроек темы"""
        with open("theme.dat", "w") as f:
            json.dump({"theme": theme_name}, f)
        self.theme = self.load_theme_settings()
        self.update_theme()

    def update_theme(self):
        """Обновление темы интерфейса"""
        self.window.configure(bg=self.theme["background"])
        for widget in self.window.winfo_children():
            if isinstance(widget, ttk.Frame):
                widget.configure(style=f'Custom.TFrame')
            elif isinstance(widget, ttk.Button):
                widget.configure(style=f'Custom.TButton')
            elif isinstance(widget, ttk.Treeview):
                widget.configure(style='Custom.Treeview')

    def load_or_generate_keys(self):
        """Загрузка или создание всех необходимых ключей"""
        keys = {}
        
        # Загрузка или создание ключа для Fernet
        if os.path.exists(self.key_files["secret.key"]) and os.path.exists(self.key_files["salt.dat"]):
            with open(self.key_files["salt.dat"], "rb") as salt_file:
                salt = salt_file.read()
            with open(self.key_files["secret.key"], "rb") as key_file:
                password = key_file.read()
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            keys["fernet_key"] = base64.urlsafe_b64encode(kdf.derive(password))
        else:
            # Генерация новой пары ключ-соль
            salt = os.urandom(16)
            password = os.urandom(32)
            
            # Сохраняем соль и пароль
            with open(self.key_files["salt.dat"], "wb") as salt_file:
                salt_file.write(salt)
            with open(self.key_files["secret.key"], "wb") as key_file:
                key_file.write(password)
                
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            keys["fernet_key"] = base64.urlsafe_b64encode(kdf.derive(password))

        # Загрузка или создание RSA ключей
        if os.path.exists(self.key_files["rsa_private.pem"]) and os.path.exists(self.key_files["rsa_public.pem"]):
            with open(self.key_files["rsa_private.pem"], "rb") as key_file:
                private_key = serialization.load_pem_private_key(
                    key_file.read(),
                    password=None,
                )
            with open(self.key_files["rsa_public.pem"], "rb") as key_file:
                public_key = serialization.load_pem_public_key(
                    key_file.read()
                )
        else:
            # Генерация новых RSA ключей
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=4096,
            )
            public_key = private_key.public_key()
            
            # Сохраняем ключи
            with open(self.key_files["rsa_private.pem"], "wb") as f:
                f.write(private_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.NoEncryption()
                ))
            with open(self.key_files["rsa_public.pem"], "wb") as f:
                f.write(public_key.public_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PublicFormat.SubjectPublicKeyInfo
                ))
        
        keys["rsa_private"] = private_key
        keys["rsa_public"] = public_key
        
        return keys

    def generate_license_key(self):
        """Генерация нового лицензионного ключа"""
        raw_uuid = str(uuid.uuid4()).replace('-', '')
        formatted_key = f"{raw_uuid[:5]}-{raw_uuid[5:10]}-{raw_uuid[10:15]}-{raw_uuid[15:20]}-{raw_uuid[20:25]}-{raw_uuid[25:30]}-{raw_uuid[30:35]}-{raw_uuid[35:]}"
        return formatted_key

    def encrypt_data(self, data):
        """Многоуровневое шифрование данных"""
        # Первый уровень: SHA-512 хеширование
        sha512_hash = hashlib.sha512(data.encode()).digest()
        
        # Второй уровень: AES шифрование через Fernet
        cipher_suite = Fernet(self.keys["fernet_key"])
        encrypted_data = cipher_suite.encrypt(data.encode())
        
        # Третий уровень: RSA шифрование
        encrypted_data = self.keys["rsa_public"].encrypt(
            encrypted_data,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA512()),
                algorithm=hashes.SHA512(),
                label=None
            )
        )
        
        # Четвертый уровень: SHA-512 хеширование результата
        final_hash = hashlib.sha512(encrypted_data).digest()
        
        # Объединение всех данных
        return base64.b64encode(encrypted_data + final_hash).decode()

    def decrypt_data(self, encrypted_data):
        """Расшифровка данных"""
        try:
            # Раскодирование Base64
            combined = base64.b64decode(encrypted_data.encode())
            
            # Разделение данных и хеша
            encrypted_data = combined[:-64]
            stored_hash = combined[-64:]
            
            # Проверка целостности данных
            current_hash = hashlib.sha512(encrypted_data).digest()
            if stored_hash != current_hash:
                raise ValueError("Данные были повреждены или подделаны")
            
            # RSA расшифровка
            decrypted_data = self.keys["rsa_private"].decrypt(
                encrypted_data,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA512()),
                    algorithm=hashes.SHA512(),
                    label=None
                )
            )
            
            # Fernet расшифровка
            cipher_suite = Fernet(self.keys["fernet_key"])
            decrypted_data = cipher_suite.decrypt(decrypted_data)
            
            return decrypted_data.decode()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось расшифровать данные: {str(e)}")
            return None

    def save_license_keys(self):
        """Сохранение ключей в зашифрованном виде с сжатием"""
        # Сжатие данных
        compressed_data = zlib.compress(json.dumps(self.license_keys).encode())
        
        # Шифрование сжатых данных
        encrypted_data = self.encrypt_data(compressed_data.decode())
        
        with open("licenses.dat", "w") as f:
            f.write(encrypted_data)

    def load_license_keys(self):
        """Загрузка сохраненных ключей"""
        if os.path.exists("licenses.dat"):
            try:
                with open("licenses.dat", "r") as f:
                    encrypted_data = f.read()
                    decrypted_data = self.decrypt_data(encrypted_data)
                    decompressed_data = zlib.decompress(decrypted_data.encode())
                    return json.loads(decompressed_data)
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось загрузить ключи: {str(e)}")
                return []
        return []

    def create_interface(self):
        """Создание интерфейса"""
        # Настройка стилей
        style = ttk.Style()
        style.configure('Custom.TFrame', background=self.theme["background"])
        style.configure('Custom.TButton', background=self.theme["button"], foreground=self.theme["text"])
        style.map('Custom.TButton', background=[('pressed', self.theme["highlight"])])
        style.configure('Custom.Treeview', background=self.theme["background"], foreground=self.theme["text"])

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
            self.tree.column(col, width=250)

        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Кнопки управления
        btn_frame = ttk.Frame(self.window)
        btn_frame.pack(fill="x", padx=10, pady=5)

        ttk.Button(btn_frame, text="Удалить выбранный ключ", command=self.delete_selected_key).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Обновить список", command=self.update_tree_view).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Копировать ключ", command=self.copy_selected_key).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Сменить тему", command=self.change_theme).pack(side="left", padx=5)

    def copy_selected_key(self):
        """Копирование выбранного ключа в буфер обмена"""
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Внимание", "Выберите ключ для копирования")
            return
        
        key = self.license_keys[self.tree.index(selected_item[0])]["key"]
        pyperclip.copy(key)
        messagebox.showinfo("Успех", "Ключ скопирован в буфер обмена")

    def change_theme(self):
        """Смена темы интерфейса"""
        current_theme = "dark" if self.theme == self.load_theme_settings()["light"] else "light"
        self.save_theme_settings(current_theme)
        messagebox.showinfo("Успех", f"Тема изменена на {current_theme}")

    def generate_and_save_key(self):
        """Генерация и сохранение нового ключа"""
        license_key = self.generate_license_key()
        date_created = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
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

    def run(self):
        """Запуск приложения"""
        self.update_tree_view()
        self.window.mainloop()

if __name__ == "__main__":
    app = LicenseManager()
    app.run()