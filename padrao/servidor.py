import websockets
import asyncio
import hashlib
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
#função quando um cliente se comunicar
async def reponse (websocket, path):
    key = await websocket.recv()
    iv = await websocket.recv()
    hash_armazenado = await websocket.recv()
    ciphertext = await websocket.recv()
    print(f"mensagem recebida:{ciphertext}")
    print(" ")

    # Descriptografando
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
    decryptor = cipher.decryptor()
    plaintext_padded = decryptor.update(ciphertext) + decryptor.finalize()
    unpadder = padding.PKCS7(128).unpadder()
    plaintext = unpadder.update(plaintext_padded) + unpadder.finalize()

    # Tirando o Hash da descriptografia
    hash_object = hashlib.sha256(plaintext)
    hash_atual = hash_object.hexdigest()
    print(hash_atual)

    # Comparando os Hash para exibição das mensagens
    if hash_atual == hash_armazenado:
        print("Mensagem recebida com sucesso!")
        decodetext = plaintext.decode('utf-8')
        print("Texto claro:", decodetext)
        resp = input("digite a resposta: ")
        await websocket.send(resp)
    else:
        print("Mensagem comprometida")

start_server = websockets.serve(reponse,'0.0.0.0',9000)
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()