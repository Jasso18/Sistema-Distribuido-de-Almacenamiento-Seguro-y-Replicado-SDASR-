import socket
import threading
import hashlib
import os
import json
from cryptography.fernet import Fernet

# Configuración
PORT = 9000
STORAGE_DIR = "/data"
# Clave fija para asegurar coincidencia
FALLBACK_KEY = b"BiZ0yWf5X2P3qRz7sJ9tV8bN1mK4lH6dG2xJ3cQ5vA8="

def get_key():
    return os.getenv("AES_KEY", FALLBACK_KEY.decode()).encode()

def decrypt_data(encrypted_data, key):
    try:
        f = Fernet(key)
        return f.decrypt(encrypted_data)
    except Exception as e:
        print(f"❌ Error Crypto: {e}")
        return None

def calculate_sha256(data):
    return hashlib.sha256(data).hexdigest()

def replicate_file(metadata, encrypted_data):
    host = os.getenv("INTERNAL_SERVICE_NAME", "storage-server-service")
    if metadata.get('is_replication'): return
    try:
        print(f"🔄 Replicando a {host}...")
        metadata['is_replication'] = True
        meta_bytes = json.dumps(metadata).encode() + b'\n'
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(5)
            s.connect((host, 9000))
            s.sendall(meta_bytes)
            s.sendall(encrypted_data)
            s.shutdown(socket.SHUT_WR) # Importante
    except Exception:
        pass # Ignoramos errores de replicación por ahora

def handle_client(conn, addr):
    print(f"🔌 Conectado: {addr}")
    try:
        # LEER METADATOS
        buffer = b""
        while b"\n" not in buffer:
            chunk = conn.recv(1024)
            if not chunk: return
            buffer += chunk
        
        header, remaining = buffer.split(b"\n", 1)
        metadata = json.loads(header.decode())
        
        # LEER ARCHIVO
        encrypted_data = remaining
        while True:
            chunk = conn.recv(4096)
            if not chunk: break
            encrypted_data += chunk
            
        # PROCESAR
        key = get_key()
        decrypted = decrypt_data(encrypted_data, key)
        
        if decrypted is None:
            conn.sendall(b"ERROR: Decryption Failed")
            return

        # VALIDAR
        if calculate_sha256(decrypted) == metadata['hash']:
            filename = metadata.get('filename', 'file.bin')
            path = os.path.join(STORAGE_DIR, filename)
            with open(path, 'wb') as f:
                f.write(decrypted)
            
            print(f"✅ Guardado: {filename}")
            conn.sendall(b"SUCCESS: File stored.")
            threading.Thread(target=replicate_file, args=(metadata, encrypted_data)).start()
        else:
            conn.sendall(b"ERROR: Hash mismatch")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        conn.close()

def start_server():
    if not os.path.exists(STORAGE_DIR): os.makedirs(STORAGE_DIR)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(('0.0.0.0', PORT))
    s.listen(5)
    print(f"🚀 Servidor listo en puerto {PORT}")
    while True:
        conn, addr = s.accept()
        threading.Thread(target=handle_client, args=(conn, addr)).start()

if __name__ == "__main__":
    start_server()