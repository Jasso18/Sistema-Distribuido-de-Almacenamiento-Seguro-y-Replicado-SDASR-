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
