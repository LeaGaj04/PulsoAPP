import os
import psycopg2
from pymongo import MongoClient
from dotenv import load_dotenv

# 1. Leer los secretos: Esto busca tu archivo .env y carga las contraseñas en la memoria sin exponerlas.
load_dotenv()
nucleo_url = os.getenv("NUCLEO_URL")
nebulosa_url = os.getenv("NEBULOSA_URL")

def probar_conexiones():
    print("Iniciando señales de radar de El Pulso...")

    # 2. Probando conexión a El Núcleo (PostgreSQL)
    try:
        conexion_nucleo = psycopg2.connect(nucleo_url)
        print(" ÉXITO: El Pulso se ha conectado a El Núcleo (PostgreSQL local).")
        conexion_nucleo.close()
    except Exception as e:
        print(f" ERROR: Falló la conexión a El Núcleo. Detalle: {e}")

    # 3. Probando conexión a La Nebulosa (MongoDB Atlas)
    try:
        cliente_mongo = MongoClient(nebulosa_url)
        # Hacemos un ping interno para forzar y verificar la conexión a internet
        cliente_mongo.admin.command('ping')
        print(" ÉXITO: El Pulso se ha conectado a La Nebulosa (MongoDB en la nube).")
        cliente_mongo.close()
    except Exception as e:
        print(f" ERROR: Falló la conexión a La Nebulosa. Detalle: {e}")

# Esta línea simplemente le dice a Python que arranque el proceso
if __name__ == "__main__":
    probar_conexiones()