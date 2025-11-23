# server.py

import socket
import threading
import hashlib
import os
import json
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from base64 import urlsafe_b64encode

# ==========================================================
# 🛡️ 1. Funciones de Criptografía y Hash (Seguridad)
# ==========================================================

# Clave precompartida. En el entorno de K8s, la cargaremos con os.getenv
# NOTA: Debes usar una clave de 32 bytes codificada en base64 para Fernet (AES).
# La clave se genera a partir de una contraseña. Aquí la cargamos directamente.

def get_key():
    """Carga la clave AES del entorno."""
    # En un entorno real, usarías Secrets de Kubernetes.
    # Por ahora, la cargamos desde una variable de entorno.
    key_b64 = os.getenv("AES_KEY", "TuClaveSecretaDe32BytesAquiParaAES256==")
    return key_b64.encode('utf-8')

def decrypt_data(encrypted_data, key):
    """Desencripta los datos usando Fernet (AES)."""
    try:
        f = Fernet(key)
        decrypted = f.decrypt(encrypted_data)
        return decrypted
    except Exception as e:
        print(f"Error al desencriptar: {e}")
        return None

def calculate_sha256(data):
    """Calcula el hash SHA-256 de los datos."""
    hasher = hashlib.sha256()
    hasher.update(data)
    return hasher.hexdigest()

# ==========================================================
# 📤 2. Lógica de Replicación (Alta Disponibilidad)
# ==========================================================

def replicate_file(metadata, encrypted_data):
    """
    Actúa como cliente para reenviar el archivo a un 'hermano'.
    Se conecta al Service de Kubernetes, el cual distribuye la carga.
    """
    # El Service Name se usa como DNS interno en Kubernetes
    SERVICE_HOST = os.getenv("INTERNAL_SERVICE_NAME", "storage-server-service")
    SERVICE_PORT = 9000  # Puerto interno expuesto por el Service

    try:
        # Crea un nuevo socket para la conexión de replicación
        replication_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        replication_socket.connect((SERVICE_HOST, SERVICE_PORT))

        # El servidor de replicación debe tener una manera de distinguir
        # entre una solicitud de cliente y una solicitud de replicación
        # Aquí, simplemente reenviamos los datos tal cual, pero en un
        # protocolo real se añadiría un indicador.
        
        # Enviamos los metadatos (hash original, nombre) como JSON
        metadata['is_replication'] = True
        replication_socket.sendall(json.dumps(metadata).encode('utf-8') + b'\n') 
        
        # Enviamos el archivo encriptado
        replication_socket.sendall(encrypted_data)
        
        print(f"✅ Archivo replicado a {SERVICE_HOST}:{SERVICE_PORT}")
        replication_socket.close()

    except Exception as e:
        print(f"❌ Error al replicar el archivo: {e}")

# ==========================================================
# 👂 3. Servidor de Sockets Principal
# ==========================================================

def handle_client(conn, addr, key):
    """Maneja la conexión de un cliente o de una réplica hermana."""
    print(f"Conexión establecida desde {addr}")

    try:
        # Recibir los metadatos (JSON que incluye el hash original)
        metadata_raw = b''
        while not metadata_raw.endswith(b'\n'):
            chunk = conn.recv(1024)
            if not chunk: break
            metadata_raw += chunk
        
        if not metadata_raw.endswith(b'\n'):
            print("Error: No se recibieron metadatos completos.")
            return

        # Separar los metadatos del resto del archivo (simplificado)
        metadata_json, encrypted_data_raw = metadata_raw.split(b'\n', 1)
        metadata = json.loads(metadata_json.decode('utf-8'))
        
        original_hash = metadata.get('hash')
        filename = metadata.get('filename', 'default_file.bin')
        is_replication = metadata.get('is_replication', False)

        # Recibir el resto de los datos encriptados
        encrypted_data = encrypted_data_raw
        while True:
            chunk = conn.recv(4096)
            if not chunk: break
            encrypted_data += chunk

        # Desencriptar los datos
        decrypted_data = decrypt_data(encrypted_data, key)

        if decrypted_data is None:
            print(f"❌ Fallo de desencriptación para {filename}. Abortando.")
            conn.sendall(b"ERROR: Decryption failed.")
            return

        # Verificar la integridad
        calculated_hash = calculate_sha256(decrypted_data)

        if calculated_hash == original_hash:
            # 1. Almacenar el archivo
            storage_path = os.path.join("/data", filename) # Asume que /data es el punto de montaje
            with open(storage_path, 'wb') as f:
                f.write(decrypted_data)
            
            status_msg = "REPLICADO" if is_replication else "ALMACENADO"
            print(f"✅ Archivo {status_msg}: {filename}. Hash OK.")
            conn.sendall(f"SUCCESS: File stored and verified ({status_msg}).".encode('utf-8'))

            # 2. Replicar solo si no es ya una solicitud de replicación
            if not is_replication:
                # Reenviar el metadata original y el archivo encriptado
                replicate_file(metadata, encrypted_data) 
        else:
            print(f"❌ Integridad fallida para {filename}. Hash esperado: {original_hash}, Recibido: {calculated_hash}")
            conn.sendall(b"ERROR: Integrity check failed.")

    except Exception as e:
        print(f"Error en la conexión con el cliente: {e}")
    finally:
        conn.close()

def start_server():
    """Inicia el servidor principal."""
    HOST = '0.0.0.0' # Escucha en todas las interfaces del contenedor
    PORT = 9000      # El puerto que expondremos

    key = get_key()
    if not key:
        print("ERROR: Clave AES no cargada. Terminando.")
        return

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # Permite reusar la dirección
    server_socket.bind((HOST, PORT))
    server_socket.listen(5)
    print(f"Servidor escuchando en {HOST}:{PORT}")
    
    # Crear el directorio de almacenamiento si no existe
    os.makedirs("/data", exist_ok=True)

    while True:
        conn, addr = server_socket.accept()
        # Usa hilos para manejar múltiples clientes simultáneamente
        client_thread = threading.Thread(target=handle_client, args=(conn, addr, key))
        client_thread.start()

if __name__ == "__main__":
    start_server()
