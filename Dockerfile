FROM python:3.9
WORKDIR /app
# Instalamos cryptography directamente
RUN pip install --no-cache-dir cryptography
COPY server.py .
RUN mkdir /data
EXPOSE 9000
CMD ["python", "-u", "server.py"]
