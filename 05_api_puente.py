import os
import psycopg2
from pymongo import MongoClient
import certifi
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# Cargamos variables de entorno (.env)
load_dotenv()
nucleo_url = os.getenv("NUCLEO_URL")
nebulosa_url = os.getenv("NEBULOSA_URL")

app = FastAPI(
    title="El Pulso API - Proyecto Púlsar",
    description="API que conecta El Núcleo (PostgreSQL) y La Nebulosa (MongoDB Atlas) para alimentar El Observatorio.",
    version="1.0.0"
)

# Configuración de CORS para permitir peticiones desde El Observatorio (Astro)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # En producción se especifica la URL de Astro (http://localhost:4321)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def obtener_conexion_nucleo():
    try:
        return psycopg2.connect(nucleo_url)
    except Exception as e:
        print(f"❌ Error al conectar con El Núcleo (PostgreSQL): {e}")
        return None

def obtener_conexion_nebulosa():
    try:
        cliente = MongoClient(nebulosa_url, tlsCAFile=certifi.where())
        return cliente
    except Exception as e:
        print(f"❌ Error al conectar con La Nebulosa (MongoDB): {e}")
        return None

@app.get("/api/v1/health")
def estado_salud():
    """Verifica el estado de salud de las conexiones a ambas dimensiones de BD."""
    conn_sql = obtener_conexion_nucleo()
    estado_sql = "OK" if conn_sql else "ERROR"
    if conn_sql:
        conn_sql.close()

    cliente_mongo = obtener_conexion_nebulosa()
    estado_mongo = "OK" if cliente_mongo else "ERROR"
    if cliente_mongo:
        cliente_mongo.close()

    return {
        "status": "ONLINE",
        "el_nucleo_postgres": estado_sql,
        "la_nebulosa_mongodb": estado_mongo
    }

@app.get("/api/v1/radar")
def obtener_catalogo_radar():
    """
    Cruza los datos rígidos de El Núcleo con los metadatos flexibles de La Nebulosa
    y los expone para El Observatorio.
    """
    conn_sql = obtener_conexion_nucleo()
    if not conn_sql:
        raise HTTPException(status_code=500, detail="Error de conexión a El Núcleo")
    
    cliente_mongo = obtener_conexion_nebulosa()
    if not cliente_mongo:
        conn_sql.close()
        raise HTTPException(status_code=500, detail="Error de conexión a La Nebulosa")

    juegos_cruzados = []

    try:
        cursor = conn_sql.cursor()
        cursor.execute("SELECT id, titulo, plataforma_base, fecha_lanzamiento FROM juegos_base;")
        juegos_base = cursor.fetchall()

        db_nebulosa = cliente_mongo["pulsar_db"]
        coleccion_metadatos = db_nebulosa["juegos_metadatos"]

        for juego in juegos_base:
            juego_id = str(juego[0])
            titulo = juego[1]
            plataforma = juego[2]
            fecha_lanza = str(juego[3]) if juego[3] else "Por anunciar"

            # Consulta cruzada en La Nebulosa
            metadatos = coleccion_metadatos.find_one({"juego_id_sql": juego_id})

            descripcion = metadatos.get("descripcion_larga", "Sin descripción disponible.") if metadatos else "Sin metadatos"
            etiquetas = metadatos.get("etiquetas", ["Indie"]) if metadatos else ["Indie"]
            devlogs = metadatos.get("devlogs", []) if metadatos else []

            juegos_cruzados.append({
                "id": juego_id,
                "titulo": titulo,
                "plataforma": plataforma,
                "fecha_lanzamiento": fecha_lanza,
                "descripcion": descripcion,
                "etiquetas": etiquetas,
                "devlogs": devlogs,
                "precio": "19.99 CRD" # Simulación transaccional de El Núcleo
            })

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error procesando cruce de datos: {str(e)}")
    finally:
        cursor.close()
        conn_sql.close()
        cliente_mongo.close()

    return {
        "total": len(juegos_cruzados),
        "juegos": juegos_cruzados
    }

@app.get("/api/v1/devlogs")
def obtener_devlogs_agregados():
    """Recopila las transmisiones de desarrolladores almacenadas en La Nebulosa."""
    cliente_mongo = obtener_conexion_nebulosa()
    if not cliente_mongo:
        raise HTTPException(status_code=500, detail="Error de conexión a La Nebulosa")

    transmisiones = []
    try:
        db_nebulosa = cliente_mongo["pulsar_db"]
        coleccion_metadatos = db_nebulosa["juegos_metadatos"]
        juegos = coleccion_metadatos.find({"devlogs": {"$exists": True, "$not": {"$size": 0}}})

        for juego in juegos:
            for log in juego.get("devlogs", []):
                transmisiones.append({
                    "juego_id": juego.get("juego_id_sql"),
                    "fecha": log.get("fecha", "2026-07-23"),
                    "titulo": log.get("titulo", "Transmisión sin título"),
                    "contenido": log.get("contenido", "")
                })

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo DevLogs: {str(e)}")
    finally:
        cliente_mongo.close()

    return {
        "total": len(transmisiones),
        "transmisiones": transmisiones
    }
