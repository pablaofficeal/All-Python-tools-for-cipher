from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
import base64

# Генерация пары ключей RSA
key = RSA.generate(2048)
private_key = key.export_key()
public_key = key.publickey().export_key()

# Функция для вычисления
def calculate(a, b, operation):
    if operation == "+":
        return a + b
    elif operation == "-":
        return a - b
    elif operation == "*":
        return a * b
    elif operation == "/":
        return a / b if b != 0 else "Ошибка: деление на ноль"
    else:
        return "Неверная операция"

# Функция шифрования результата с AES
def encrypt_result(result, rsa_public_key):
    # Генерация симметричного ключа AES
    aes_key = get_random_bytes(16)
    cipher_aes = AES.new(aes_key, AES.MODE_EAX)
    ciphertext, tag = cipher_aes.encrypt_and_digest(str(result).encode())

    # Шифрование AES-ключа с помощью RSA
    rsa_key = RSA.import_key(rsa_public_key)
    cipher_rsa = PKCS1_OAEP.new(rsa_key)
    encrypted_aes_key = cipher_rsa.encrypt(aes_key)

    return base64.b64encode(encrypted_aes_key).decode(), base64.b64encode(ciphertext).decode()

# Пример использования
a = int(input("Введите первое число: "))
b = int(input("Введите второе число: "))
operation = input("Введите операцию (+, -, *, /): ")

result = calculate(a, b, operation)
print("Результат:", result)

enc_key, enc_result = encrypt_result(result, public_key)
print("\nЗашифрованный результат:", enc_result)
print("Зашифрованный AES-ключ:", enc_key)
