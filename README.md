# 📂 Sistema Distribuido de Almacenamiento Seguro y Replicado (SDASR)

Este proyecto implementa un servicio de almacenamiento de archivos seguro y altamente disponible utilizando **Sockets en Python**, **Docker** y un clúster de **Kubernetes (Minikube)**.

El sistema garantiza:
1.  **Confidencialidad:** Encriptación AES-256 antes de la transmisión.
2.  **Integridad:** Verificación mediante Hash SHA-256.
3.  **Disponibilidad:** Replicación automática de archivos entre nodos del clúster.

---

## 🚀 Tecnologías Utilizadas

* **Lenguaje:** Python 3.9
* **Contenedores:** Docker
* **Orquestación:** Kubernetes (Minikube)
* **Librerías Clave:** `cryptography`, `socket`, `hashlib`
* **Comunicación:** Protocolo TCP personalizado

---

## ⚙️ Prerrequisitos

Para ejecutar este proyecto necesitas tener instalado:
* Python 3
* Docker Desktop
* Minikube
* kubectl

---

## 🛠️ Instrucciones de Despliegue (Paso a Paso)

### 1. Clonar el repositorio
```bash
git clone [https://github.com/Jasso18/Sistema-Distribuido-de-Almacenamiento-Seguro-y-Replicado-SDASR-.git](https://github.com/Jasso18/Sistema-Distribuido-de-Almacenamiento-Seguro-y-Replicado-SDASR-.git)
cd Sistema-Distribuido-de-Almacenamiento-Seguro-y-Replicado-SDASR-
2.  **Construir la Imagen en Minikube:**
    ```bash
    eval $(minikube docker-env)
    docker build -t file-storage-server:v1 .
    ```

3.  **Desplegar en Kubernetes:**
    ```bash
    kubectl apply -f deployment.yaml
    kubectl apply -f service.yaml
    ```

4.  **Verificar estado:**
    ```bash
    kubectl get pods
    ```

## 💻 Uso (Cliente)

Para enviar un archivo al clúster, utiliza el script del cliente.

**Ejemplo local (con Port-Forwarding):**
```bash
# En una terminal (Túnel):
kubectl port-forward service/storage-server-service 8080:9000

# En otra terminal (Cliente):
python3 client.py 127.0.0.1 8080 mi_archivo_secreto.txt
---

## 📡 Parte 2: Guía para Ejecutar en 2 Dispositivos (Demo Real)

Para impresionar a tu profesor, vamos a simular un entorno real.
* **PC 1 (Servidor):** Tu computadora con Minikube.
* **PC 2 (Cliente):** Otra computadora (laptop, la del profesor, etc.) o incluso tu celular (usando Termux), conectada a la **misma red Wi-Fi**.



[Image of network diagram connecting client PC to server PC running Kubernetes]


### Pasos en la PC 1 (La tuya / Servidor)

1.  **Averigua tu dirección IP local:**
    * En Windows (Terminal): `ipconfig` (Busca "Dirección IPv4" en tu adaptador Wi-Fi. Ej: `192.168.1.50`).
    * En Linux/Mac: `hostname -I`.
    * *Anotala, la llamaremos `IP_SERVIDOR`.*

2.  **Abre el Túnel Público:**
    Normalmente el túnel solo escucha en tu propia máquina. Usaremos el truco `--address 0.0.0.0` para decirle que acepte conexiones de **cualquier** dispositivo en la red.

    ```bash
    # Ejecuta esto y NO cierres la terminal
    kubectl port-forward --address 0.0.0.0 service/storage-server-service 8080:9000
    ```
    *Debería decir: `Forwarding from 0.0.0.0:8080 -> 9000`.*

### Pasos en la PC 2 (La otra / Cliente)

1.  **Obtener el Cliente:**
    Descarga el archivo `client.py` de tu GitHub o pásalo por USB/Correo a esta computadora.

2.  **Instalar Python y Dependencias:**
    Esa computadora debe tener Python instalado. Abre su terminal y ejecuta:
    ```bash
    pip install cryptography
    ```
    *(Si no tienen Python, no funcionará. Asegúrate de que tenga Python).*

3.  **¡Lanzar el Archivo! 🚀**
    Desde la terminal de la PC 2, ejecuta el cliente apuntando a la IP de la PC 1.

    ```bash
    # Sintaxis: python client.py <IP_SERVIDOR> 8080 <ARCHIVO>
    # Ejemplo real (usando la IP que anotaste):
    python client.py 192.168.1.50 8080 foto_vacaciones.jpg
    ```

### ¿Qué sucederá?

1.  La **PC 2** encriptará el archivo.
2.  Los datos viajarán por el Wi-Fi hasta la **PC 1**.
3.  El túnel de la **PC 1** recibirá los datos y los meterá dentro de Kubernetes.
4.  El Pod guardará el archivo.
5.  La **PC 2** recibirá el mensaje: `SUCCESS: File stored`.

¡Si logras esto, tendrás un sistema distribuido real funcionando en red! Suerte
