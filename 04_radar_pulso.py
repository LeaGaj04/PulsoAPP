import os
import psycopg2
from pymongo import MongoClient
from dotenv import load_dotenv

# Cargamos las llaves de nuestras bóvedas
load_dotenv()
nucleo_url = os.getenv("NUCLEO_URL")
nebulosa_url = os.getenv("NEBULOSA_URL")

def escanear_radar():
    print("Iniciando escáner de El Pulso...\n")
    
    # 1. Conectamos a ambas dimensiones
    conn_nucleo = psycopg2.connect(nucleo_url)
    cursor = conn_nucleo.cursor()
    cliente_mongo = MongoClient(nebulosa_url)
    db_nebulosa = cliente_mongo["pulsar_db"]
    coleccion_metadatos = db_nebulosa["juegos_metadatos"]

    try:
        # 2. Extraemos el dato duro de El Núcleo (PostgreSQL)
        cursor.execute("SELECT id, titulo, plataforma_base FROM juegos_base;")
        juegos_rigidos = cursor.fetchall()

        for juego in juegos_rigidos:
            juego_id = juego[0]
            titulo = juego[1]
            plataforma = juego[2]

            print(f"🌟 Joya detectada en El Núcleo: {titulo} ({plataforma})")

            # 3. Cruzamos la información: Buscamos en La Nebulosa (MongoDB) usando el ID relacional
            metadatos = coleccion_metadatos.find_one({"juego_id_sql": str(juego_id)})

            if metadatos:
                descripcion = metadatos.get("descripcion_larga", "Sin descripción")
                etiquetas = ", ".join(metadatos.get("etiquetas", []))
                print(f"   - Etiquetas (La Nebulosa): {etiquetas}")
                print(f"   - Descripción: {descripcion[:60]}...\n")
            else:
                print("   - No se encontraron metadatos en La Nebulosa para este título.\n")

    except Exception as e:
        print(f"❌ ERROR durante el escaneo: {e}")
    
    finally:
        # Apagamos las conexiones de forma segura
        cursor.close()
        conn_nucleo.close()
        cliente_mongo.close()

if __name__ == "__main__":
    escanear_radar()