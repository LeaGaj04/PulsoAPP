import os
import psycopg2
from pymongo import MongoClient
from dotenv import load_dotenv

# Cargamos nuestras contraseñas seguras
load_dotenv()
nucleo_url = os.getenv("NUCLEO_URL")
nebulosa_url = os.getenv("NEBULOSA_URL")

def insertar_joya_indie():
    print("Iniciando inyección de Contenido Semilla en Púlsar...")
    
    # 1. Conectamos a ambas bases de datos
    conn_nucleo = psycopg2.connect(nucleo_url)
    cursor = conn_nucleo.cursor()
    cliente_mongo = MongoClient(nebulosa_url)
    db_nebulosa = cliente_mongo["pulsar_db"] # Nombramos nuestra base de datos en MongoDB
    coleccion_metadatos = db_nebulosa["juegos_metadatos"]

    try:
        # 2. Guardamos en El Núcleo (Datos Rígidos)
        # Primero creamos un usuario desarrollador simulado
        cursor.execute("""
            INSERT INTO usuarios (nombre_usuario, correo, password_hash, tipo_cuenta)
            VALUES ('HollowStudio', 'contacto@hollow.com', 'hash_falso_123', 'desarrollador')
            RETURNING id;
        """)
        dev_id = cursor.fetchone()[0]

        # Luego registramos el juego base asociado a ese desarrollador
        cursor.execute("""
            INSERT INTO juegos_base (desarrollador_id, titulo, plataforma_base, fecha_lanzamiento)
            VALUES (%s, 'Sombras del Vacío', 'PC', '2026-10-31')
            RETURNING id;
        """, (dev_id,))
        juego_id = cursor.fetchone()[0] # ¡Este UUID es vital!

        # Guardamos los cambios en PostgreSQL
        conn_nucleo.commit()
        print(f" El Núcleo: Juego base registrado con ID {juego_id}")

        # 3. Guardamos en La Nebulosa (Datos Flexibles)
        # Usamos el MISMO ID generado por SQL para vincular los metadatos complejos
        metadatos_juego = {
            "juego_id_sql": str(juego_id),
            "descripcion_larga": "Un metroidvania oscuro donde exploras las profundidades de un planeta olvidado...",
            "etiquetas": ["Metroidvania", "Dark Fantasy", "Pixel Art", "Difícil"],
            "requerimientos_sistema": {
                "os": "Windows 10",
                "ram": "8GB",
                "grafica": "GTX 1060"
            },
            "devlogs": [
                {"fecha": "2026-07-10", "titulo": "Mejorando el sistema de saltos", "contenido": "Hoy pasamos 10 horas ajustando la gravedad..."}
            ]
        }
        
        coleccion_metadatos.insert_one(metadatos_juego)
        print(f"✅ La Nebulosa: Metadatos y DevLogs guardados exitosamente.")

    except Exception as e:
        print(f" ERROR durante la inserción: {e}")
        conn_nucleo.rollback() # Si algo falla, deshacemos los cambios para evitar datos corruptos
    
    finally:
        # Cerramos las puertas de nuestras bóvedas
        cursor.close()
        conn_nucleo.close()
        cliente_mongo.close()

if __name__ == "__main__":
    insertar_joya_indie()