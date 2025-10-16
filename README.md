# cine_mood

## Ejecución en Local

### Prerequisitos

Para esta option es necesario tener:

+ Una clave de [API de Google (Gemini)](https://aistudio.google.com/api-keys).

+ Una clave de [API de The Movie Database (TMDb)](https://www.themoviedb.org/settings/api).


### Backend
Navega a ```/backend```.

Crea y activa un entorno virtual: 
```
python -m venv venv
```
Para macOS:
```
source venv/bin/activate
```
Para Windows:
```
.venv\Scripts\activate
```

Crea el archivo .env, este archivo debe de contener:
```
GOOGLE_API_KEY="Your_google_api_key"
TMDB_API_KEY="Your_TMDB_api_key"
```

Instala las dependencias: 
```
pip install -r requirements.txt
```

Ejecuta el servidor: 
```
uvicorn main:app --reload
```

Para la opcion de utilizar la API de OpenAI:
```
uvicorn use_openai:app --reload
```
> :warning: Cuidaddo, debido a que el uso del API de OpenAI no es gratuito, esta opcion no se a testeado!
   

### Frontend

Navega a ```/frontend```.


Instala las dependencias:

```
npm install
```

Ejecuta la aplicación de desarrollo:

```
npm run dev
```

Abre [http://localhost:3000](http://localhost:3000/) en tu navegador.


---

## Ejecución en Docker

### Prerequisitos

Para esta option es necesario tener:

+ [Docker Desktop](https://www.docker.com/products/docker-desktop/) instalado

+ Una clave de [API de Google (Gemini)](https://aistudio.google.com/api-keys).

+ Una clave de [API de The Movie Database (TMDb)](https://www.themoviedb.org/settings/api).


Crea el archivo ```.env``` desde ```/backend```, este archivo debe de contener:
```
GOOGLE_API_KEY="Your_google_api_key"
TMDB_API_KEY="Your_TMDB_api_key"
```

Desde la raiz del proyecto, ejecuta:
```
docker-compose up --build
```

Esta option puede tardar aproximadamente 3-5min
