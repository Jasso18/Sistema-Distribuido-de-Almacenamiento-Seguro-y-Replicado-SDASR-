import socket
import sys
import os
import json
import hashlib
from cryptography.fernet import Fernet

# LA MISMA CLAVE QUE EL SERVIDOR
DEFAULT_KEY = b"BiZ0yWf5X2P3qRz7sJ9tV8bN1mK4lH6dG2xJ3cQ5vA8="

def send_file(host, port, filepath):
    # Encriptar
    with open(filepath, 'rb') as f: data = f.read()
    file_hash = hashlib.sha256(data).hexdigest()
    f_enc = Fernet(DEFAULT_KEY)
    encrypted_data = f_enc.encrypt(data)
    
    # Preparar Metadata
    metadata = {"filename": os.path.basename(filepath), "hash": file_hash, "is_replication": False}
    meta_bytes = json.dumps(metadata).encode() + b'\n'

    # Enviar
    print(f"📡 Enviando a {host}:{port}...")
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((host, int(port)))
            s.sendall(meta_bytes)
            s.sendall(encrypted_data)
            s.shutdown(socket.SHUT_WR) # AVISAR AL SERVIDOR QUE TERMINAMOS
            
            response = s.recv(1024)
            print(f"📨 Respuesta: {response.decode()}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    send_file(sys.argv[1], sys.argv[2], sys.argv[3])