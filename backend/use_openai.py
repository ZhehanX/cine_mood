import os
import requests
from openai import OpenAI
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
app = FastAPI(title="CineMood API con TMDb y OpenAI")
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

        # 1. Obtener la lista completa de géneros de TMDb
        genre_url = f"https://api.themoviedb.org/3/genre/movie/list?api_key={tmdb_api_key}&language=es-ES"
        genre_response = requests.get(genre_url)
        genre_response.raise_for_status()
        all_genres = genre_response.json()["genres"]
        genre_map = {genre['id']: genre['name'] for genre in all_genres}

        # 2. Consultar a OpenAI para obtener un género
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if not openai_api_key:
            raise HTTPException(status_code=500, detail="La clave API de OpenAI no está configurada.")
        
        openai_client = OpenAI(api_key=openai_api_key)
        
        print("-> Consultando OpenAI...")
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Extrae un solo género cinematográfico en español del texto del usuario. Responde solo con el nombre del género (ej: 'Comedia', 'Ciencia ficción', 'Terror')."},
                {"role": "user", "content": user_input.prompt}
            ],
            temperature=0.2,
            max_tokens=15
        )
        search_term = response.choices[0].message.content.strip().lower()
        print(f"-> Género de OpenAI: '{search_term}'")

        # Buscamos el ID del género que obtuvimos
        genre_id = None
        searched_genre_name = None
        for g_id, g_name in genre_map.items():
            if g_name.lower() == search_term:
                genre_id = g_id
                searched_genre_name = g_name
                break
        
        # 3. Descubrir películas basadas en el género o la palabra clave
        if not genre_id:
            print(f"No se encontró ID para '{search_term}'. Buscando por palabra clave.")
            discover_url = f"https://api.themoviedb.org/3/search/movie?api_key={tmdb_api_key}&query={search_term}&language=es-ES&page=1&include_adult=false"
        else:
            print(f"-> ID de género encontrado: {genre_id}. Buscando películas populares.")
            discover_url = f"https://api.themoviedb.org/3/discover/movie?api_key={tmdb_api_key}&with_genres={genre_id}&sort_by=popularity.desc&language=es-ES&page=1&include_adult=false"

        movies_response = requests.get(discover_url)
        movies_response.raise_for_status()
        movies_data = movies_response.json()["results"]

        # 4. Formatear la respuesta, asegurando que el género buscado aparezca primero
        formatted_movies = []
        for movie in movies_data[:10]:
            if movie.get("poster_path"):
                movie_genres_from_api = [genre_map.get(g_id) for g_id in movie.get("genre_ids", []) if genre_map.get(g_id)]
                
                final_genres = []
                if searched_genre_name:
                    final_genres.append(searched_genre_name)
                    for g in movie_genres_from_api:
                        if g != searched_genre_name:
                            final_genres.append(g)
                else:
                    final_genres = movie_genres_from_api

                formatted_movies.append({
                    "id": movie.get("id"),
                    "title": movie.get("title"),
                    "overview": movie.get("overview", "Sin descripción."),
                    "poster_url": f"https://image.tmdb.org/t/p/w500{movie.get('poster_path')}",
                    "year": movie.get("release_date", "----")[:4],
                    "genres": final_genres[:3]
                })
        
        return {"movies": formatted_movies}

    except Exception as e:
        print("\n!!!!!! ERROR INESPERADO ATRAPADO !!!!!!")
        traceback.print_exc()
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"Ocurrió un error interno: {str(e)}")

