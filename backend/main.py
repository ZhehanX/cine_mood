import os
import requests
import google.generativeai as genai
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import traceback

# Cargar variables de entorno
load_dotenv()

# --- Modelos de Datos ---
class UserInput(BaseModel):
    prompt: str

# --- Configuración de la App FastAPI ---
app = FastAPI(title="CineMood API con TMDb y Gemini")
origins = ["http://localhost:3000"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Endpoint de Recomendación ---
@app.post("/recommend")
def recommend_movie(user_input: UserInput):
    try:
        if not user_input.prompt:
            raise HTTPException(status_code=400, detail="El prompt no puede estar vacío.")

        tmdb_api_key = os.getenv("TMDB_API_KEY")
        if not tmdb_api_key:
             raise HTTPException(status_code=500, detail="La clave API de TMDb no está configurada.")

        # 1. Obtener la lista completa de géneros de TMDb y crear un mapa de ID -> Nombre
        genre_url = f"https://api.themoviedb.org/3/genre/movie/list?api_key={tmdb_api_key}&language=es-ES"
        genre_response = requests.get(genre_url)
        genre_response.raise_for_status()
        all_genres = genre_response.json()["genres"]
        genre_map = {genre['id']: genre['name'] for genre in all_genres}

        # 2. Consultar a Gemini para obtener un género del prompt del usuario
        google_api_key = os.getenv("GOOGLE_API_KEY")
        if not google_api_key:
            raise HTTPException(status_code=500, detail="La clave API de Google no está configurada.")
        
        genai.configure(api_key=google_api_key)
        model = genai.GenerativeModel('gemini-2.5-flash')
        

        prompt_template = f"""

            Tu única tarea es extraer una sola palabra clave (un género o tema cinematográfico) en español del texto de un usuario.
            Responde solo y únicamente con esa palabra, sin puntuación ni texto adicional.
            Ejemplo 1: si el usuario dice 'quiero algo de risa', tu respuesta debe ser exactamente 'comedia'.
            Ejemplo 2: si el usuario dice 'naves espaciales y el futuro', tu respuesta debe ser exactamente 'ciencia ficción'.
            Ejemplo 3: si el usuario dice 'miedo y sustos', tu respuesta debe ser 'terror'.

            Texto del usuario: '{user_input.prompt}'
        """

        print("-> Consultando Gemini...")
        response = model.generate_content(prompt_template)
        genre_name = response.text.strip().lower()
        print(f"-> Género de Gemini: '{genre_name}'")

        # Buscamos el ID del género que nos dio Gemini
        genre_id = None
        searched_genre_name = None
        for g_id, g_name in genre_map.items():
            if g_name.lower() == genre_name:
                genre_id = g_id
                searched_genre_name = g_name
                break
        
        # 3. Descubrir películas basadas en el género o la palabra clave
        if not genre_id:
            print(f"No se encontró ID para '{genre_name}'. Buscando por palabra clave.")
            discover_url = f"https://api.themoviedb.org/3/search/movie?api_key={tmdb_api_key}&query={genre_name}&language=es-ES&page=1&include_adult=false"
        else:
            print(f"-> ID de género encontrado: {genre_id}. Buscando películas populares.")
            discover_url = f"https://api.themoviedb.org/3/discover/movie?api_key={tmdb_api_key}&with_genres={genre_id}&sort_by=popularity.desc&language=es-ES&page=1&include_adult=false"

        print(f"-> Consultando TMDb: {discover_url}")
        movies_response = requests.get(discover_url)
        movies_response.raise_for_status()
        movies_data = movies_response.json()["results"]

        # 4. Formatear la respuesta, incluyendo los nombres de los géneros
        formatted_movies = []
        for movie in movies_data[:10]:
            if movie.get("poster_path"):
                
                # Obtenemos los géneros que TMDb nos da
                movie_genres_from_api = [genre_map.get(g_id) for g_id in movie.get("genre_ids", []) if genre_map.get(g_id)]
                
                final_genres = []
                # --- NUEVA LÓGICA DE PRIORIZACIÓN DE GÉNERO ---
                if searched_genre_name:
                    # 1. Añadimos el género buscado primero
                    final_genres.append(searched_genre_name)
                    # 2. Añadimos otros géneros que no sean el buscado, para evitar duplicados
                    for g in movie_genres_from_api:
                        if g != searched_genre_name:
                            final_genres.append(g)
                else:
                    # Si no buscamos por un género específico, mostramos los que vienen de la API
                    final_genres = movie_genres_from_api
                
                formatted_movies.append({
                    "id": movie.get("id"),
                    "title": movie.get("title"),
                    "overview": movie.get("overview", "Sin descripción."),
                    "poster_url": f"https://image.tmdb.org/t/p/w500{movie.get('poster_path')}",
                    "year": movie.get("release_date", "----")[:4],
                    "genres": final_genres[:3] # Devolvemos un máximo de 3 géneros
                })
        
        return {"movies": formatted_movies}

    except Exception as e:
        print("\n!!!!!! ERROR INESPERADO ATRAPADO !!!!!!")
        traceback.print_exc()
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"Ocurrió un error interno: {str(e)}")

