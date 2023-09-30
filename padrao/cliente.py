import websockets
import asyncio
import hashlib
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
import os

async def authenticate_user():
    tentativas_max = 3
    tentativa_atual = 0
    users = {
        "santiago": "063688",
        "kauan": "987654"
    }
    authenticated = False

    while (tentativa_atual < tentativas_max):
        user = input("Digite o usuário: ").lower().strip()

        if user in users and users[user] == input("Digite a senha: ").strip():
            print("Acesso autorizado")
            authenticated = True
            break
        else:
            tentativa_atual += 1
            restante = tentativas_max - tentativa_atual

            if restante > 0:
                print("Usuário ou senha incorreta, tentativas restantes ", restante)
            else:
                print("Número de tentativas excedidas. Acesso bloqueado!")
                break

    return authenticated

async def send_messages():
    authenticated = await authenticate_user()

    if not authenticated:
        return

    async with websockets.connect("ws://localhost:8000") as socket:
        while True:
            msn = input("Digite uma mensagem para o servidor (ou 'sair' para encerrar): ")

            if msn.lower() == 'sair':
                await socket.close()
                break

            # Calcular o hash da mensagem
            hash_object = hashlib.sha256()
            hash_object.update(msn.encode('utf-8'))
            hash_hex = hash_object.hexdigest()
            hash_armazenado = hash_hex

            # Preparando a criptografia
            key = os.urandom(32)
            iv = os.urandom(16)
            cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
            msn_bytes = msn.encode('utf-8')
            padder = padding.PKCS7(128).padder()
            msn_bytes_padded = padder.update(msn_bytes) + padder.finalize()
            encryptor = cipher.encryptor()
            ciphertext = encryptor.update(msn_bytes_padded) + encryptor.finalize()

            await socket.send(key)
            await socket.send(iv)
            await socket.send(hash_armazenado)
            await socket.send(ciphertext)
            print(await socket.recv())
asyncio.get_event_loop().run_until_complete(send_messages())
asyncio.get_event_loop().run_forever()

