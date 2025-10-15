import os
import requests
from openai import OpenAI
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Cargar variables de entorno desde el archivo .env
load_dotenv()

# --- Modelos de Datos (Pydantic) ---
class UserInput(BaseModel):
    prompt: str

# --- Configuración de la App FastAPI ---
app = FastAPI(
    title="CineMood API",
    description="Una API para recomendar películas basadas en el estado de ánimo del usuario."
)

# --- Configuración de CORS ---
origins = [
    "http://localhost:3000", 
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Clientes de API ---
try:
    openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    OMDB_API_KEY = os.getenv("OMDB_API_KEY")
    if not OMDB_API_KEY:
        raise ValueError("La clave de API de OMDb no se encontró en las variables de entorno.")
except Exception as e:
    print(f"Error inicializando clientes de API: {e}")
    

# --- Endpoint de Recomendación ---
@app.post("/recommend")
def recommend_movie(user_input: UserInput):
    """
    Recibe el texto de un usuario, extrae una palabra clave con OpenAI
    y busca películas en OMDb.
    """
    if not user_input.prompt:
        raise HTTPException(status_code=400, detail="El texto de entrada no puede estar vacío.")

    # 1. Consultar a OpenAI para obtener una palabra clave
    try:
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Eres un asistente experto en cine. Tu única tarea es extraer una sola palabra clave o género cinematográfico en español del texto del usuario. Responde solo con esa palabra, sin puntuación ni texto adicional. Por ejemplo, si el usuario dice 'quiero algo de risa', responde 'comedia'. Si dice 'naves espaciales y futuro', responde 'sci-fi'."},
                {"role": "user", "content": user_input.prompt}
            ],
            temperature=0.2,
            max_tokens=10
        )
        keyword = response.choices[0].message.content.strip().lower()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al contactar con la API de OpenAI: {e}")

    if not keyword:
        raise HTTPException(status_code=404, detail="No se pudo extraer una palabra clave del texto.")

    # 2. Usar la palabra clave para buscar en OMDb
    omdb_url = f"http://www.omdbapi.com/?apikey={OMDB_API_KEY}&s={keyword}&type=movie"
    try:
        omdb_response = requests.get(omdb_url)
        omdb_response.raise_for_status()  # Lanza un error para respuestas HTTP 4xx/5xx
        data = omdb_response.json()

        if data.get("Response") == "True":
            # Devolvemos solo la lista de películas para que el frontend la procese
            return {"movies": data.get("Search", [])}
        else:
            # Si OMDb no encuentra nada, devolvemos una lista vacía
            return {"movies": []}

    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Error al contactar con la API de OMDb: {e}")

# --- Endpoint Raíz para verificar que la API funciona ---
@app.get("/")
def read_root():
    return {"status": "CineMood API está en funcionamiento"}