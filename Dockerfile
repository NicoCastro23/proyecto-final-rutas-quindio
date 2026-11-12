FROM python:3.13-slim
# Imagen opcional de R5; la vía principal es el entorno virtual (ver README).
WORKDIR /app
# Primero las dependencias: así Docker reutiliza esta capa si solo cambia el código.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY rutas/ rutas/
COPY data/catalogo.csv data/catalogo.csv
COPY data/processed/ data/processed/
COPY results/ results/
EXPOSE 5050
# 0.0.0.0 para que el puerto publicado con -p sea alcanzable desde fuera del contenedor.
CMD ["python", "-m", "rutas.r5.app", "--host", "0.0.0.0", "--puerto", "5050"]
