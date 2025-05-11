import customtkinter as ctk
from tkinter import messagebox
import secrets
import string
import os
from cryptography.fernet import Fernet

# Файлы для истории
PASSWORD_FILE = "passwords.enc"
EMAIL_FILE = "emails.enc"
KEY_FILE = "secret.key"

# Генерация ключа шифрования
def generate_key():
    if not os.path.exists(KEY_FILE):
        key = Fernet.generate_key()
        with open(KEY_FILE, "wb") as key_file:
            key_file.write(key)

# Загрузка ключа шифрования
def load_key():
    return open(KEY_FILE, "rb").read()

# Шифрование данных
def encrypt_data(data, key):
    fernet = Fernet(key)
    return fernet.encrypt(data.encode())

# Дешифрование данных
def decrypt_data(encrypted_data, key):
    fernet = Fernet(key)
    return fernet.decrypt(encrypted_data).decode()

class PasswordGeneratorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("SSL Password Generator")
        self.root.geometry("420x500")
        self.root.configure(bg="#212121")

        # Создание вкладок
        self.notebook = ctk.CTkTabview(root)
        self.notebook.pack(expand=True, fill="both")

        # Вкладка для паролей
        self.password_frame = self.notebook.add("Генератор паролей")

        # Вкладка для почт
        self.email_frame = self.notebook.add("Генератор почт")

        self.create_password_tab()  # Создание вкладки для паролей
        self.create_email_tab()    # Создание вкладки для почт

        # Генерация и загрузка ключа шифрования
        generate_key()
        self.key = load_key()

    def create_password_tab(self):
        ctk.CTkLabel(self.password_frame, text="Выберите длину пароля:", font=("Arial", 12)).pack(pady=5)

        self.password_length = ctk.IntVar(value=12)
        self.length_dropdown = ctk.CTkComboBox(
            self.password_frame, 
            variable=self.password_length, 
            values=[str(x) for x in [8, 12, 16, 20, 24, 32, 48]],  # Преобразуем числа в строки
            state="readonly"
        )
        self.length_dropdown.pack(pady=5)

        self.generate_password_button = ctk.CTkButton(self.password_frame, text="Сгенерировать пароль", command=self.generate_password)
        self.generate_password_button.pack(pady=5)

        ctk.CTkLabel(self.password_frame, text="Сгенерированный пароль:", font=("Arial", 12)).pack(pady=5)
        self.password_entry = ctk.CTkEntry(self.password_frame, font=("Arial", 12), state="readonly", width=30)
        self.password_entry.pack(pady=5)

        self.show_password_history_button = ctk.CTkButton(self.password_frame, text="Показать историю паролей", command=self.show_password_history)
        self.show_password_history_button.pack(pady=5)

    def create_email_tab(self):
        ctk.CTkLabel(self.email_frame, text="Имя:", font=("Arial", 12)).pack(pady=5)
        self.name_entry = ctk.CTkEntry(self.email_frame, font=("Arial", 12), width=30)
        self.name_entry.pack(pady=5)

        ctk.CTkLabel(self.email_frame, text="Фамилия:", font=("Arial", 12)).pack(pady=5)
        self.surname_entry = ctk.CTkEntry(self.email_frame, font=("Arial", 12), width=30)
        self.surname_entry.pack(pady=5)

        ctk.CTkLabel(self.email_frame, text="Любимое число:", font=("Arial", 12)).pack(pady=5)
        self.favorite_number_entry = ctk.CTkEntry(self.email_frame, font=("Arial", 12), width=30)
        self.favorite_number_entry.pack(pady=5)

        self.generate_email_button = ctk.CTkButton(self.email_frame, text="Сгенерировать почту", command=self.generate_email)
        self.generate_email_button.pack(pady=5)

        ctk.CTkLabel(self.email_frame, text="Сгенерированная почта:", font=("Arial", 12)).pack(pady=5)
        self.email_entry = ctk.CTkEntry(self.email_frame, font=("Arial", 12), state="readonly", width=30)
        self.email_entry.pack(pady=5)

        self.show_email_history_button = ctk.CTkButton(self.email_frame, text="Показать историю почт", command=self.show_email_history)
        self.show_email_history_button.pack(pady=5)

    def generate_password(self):
        length = self.password_length.get()
        alphabet = string.ascii_letters + string.digits + string.punctuation
        password = ''.join(secrets.choice(alphabet) for _ in range(length))

        self.password_entry.configure(state="normal")
        self.password_entry.delete(0, ctk.END)
        self.password_entry.insert(0, password)
        self.password_entry.configure(state="readonly")

        encrypted_password = encrypt_data(password, self.key)
        with open(PASSWORD_FILE, "ab") as file:
            file.write(encrypted_password + b"\n")

    def generate_email(self):
        name = self.name_entry.get().strip()
        surname = self.surname_entry.get().strip()
        favorite_number = self.favorite_number_entry.get().strip()

        if not name or not surname or not favorite_number:
            messagebox.showerror("Ошибка", "Заполните все поля для генерации почты.")
            return

        email = f"{name.lower()}.{surname.lower()}{favorite_number}@gmail.com"

        self.email_entry.configure(state="normal")
        self.email_entry.delete(0, ctk.END)
        self.email_entry.insert(0, email)
        self.email_entry.configure(state="readonly")

        encrypted_email = encrypt_data(email, self.key)
        with open(EMAIL_FILE, "ab") as file:
            file.write(encrypted_email + b"\n")

    def show_password_history(self):
        if not os.path.exists(PASSWORD_FILE):
            messagebox.showinfo("История паролей", "История паролей пуста.")
            return

        with open(PASSWORD_FILE, "rb") as file:
            encrypted_history = file.readlines()

        decrypted_history = [decrypt_data(line.strip(), self.key) for line in encrypted_history]
        messagebox.showinfo("История паролей", "\n".join(decrypted_history) if decrypted_history else "История паролей пуста.")

    def show_email_history(self):
        if not os.path.exists(EMAIL_FILE):
            messagebox.showinfo("История почт", "История почт пуста.")
            return

        with open(EMAIL_FILE, "rb") as file:
            encrypted_history = file.readlines()

        decrypted_history = [decrypt_data(line.strip(), self.key) for line in encrypted_history]
        messagebox.showinfo("История почт", "\n".join(decrypted_history) if decrypted_history else "История почт пуста.")

if __name__ == "__main__":
    root = ctk.CTk()
    app = PasswordGeneratorApp(root)
    root.mainloop()