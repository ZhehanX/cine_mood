'use client'; // Directiva para indicar que es un componente de cliente en Next.js App Router

import { useState } from 'react';
import axios from 'axios';
import MovieCard from './components/Movie_card'; 

// Definimos la 'forma' de los datos de una película
interface Movie {
  Title: string;
  Year: string;
  imdbID: string;
  Type: string;
  Poster: string;
}

export default function HomePage() {
  const [prompt, setPrompt] = useState('');
  const [movies, setMovies] = useState<Movie[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!prompt.trim()) {
      setError('Por favor, describe cómo te sientes.');
      return;
    }
    
    setIsLoading(true);
    setError(null);
    setMovies([]);

    try {
      const response = await axios.post('http://127.0.0.1:8000/recommend', { prompt });
      if (response.data.movies && response.data.movies.length > 0) {
        setMovies(response.data.movies);
      } else {
        setError('No encontramos películas para esa descripción. ¡Intenta con otra!');
      }
    } catch (err) {
      setError('Ocurrió un error al buscar recomendaciones. Por favor, inténtalo de nuevo.');
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <main className="min-h-screen bg-gray-900 text-white p-8">
      <div className="container mx-auto max-w-4xl text-center">
        <h1 className="text-5xl font-bold mb-4">🎬 CineMood</h1>
        <p className="text-xl text-gray-400 mb-8">¿Cómo te sientes hoy?</p>
        
        <form onSubmit={handleSubmit} className="mb-12">
          <input
            type="text"
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            placeholder="Ej: 'Me siento aventurero y quiero ver mucha acción.'"
            className="w-full max-w-xl p-4 rounded-lg bg-gray-800 border border-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500 transition"
          />
          <button
            type="submit"
            disabled={isLoading}
            className="mt-4 px-8 py-3 bg-blue-600 rounded-lg font-semibold hover:bg-blue-700 transition disabled:bg-gray-500 disabled:cursor-not-allowed"
          >
            {isLoading ? 'Buscando...' : 'Encuentra mi película'}
          </button>
        </form>

        {error && <p className="text-red-500 text-lg">{error}</p>}

        {movies.length > 0 && (
          <div>
            <h2 className="text-3xl font-bold mb-6">Aquí tienes algunas recomendaciones:</h2>
            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-8">
              {movies.map((movie) => (
                <MovieCard key={movie.imdbID} movie={movie} />
              ))}
            </div>
          </div>
        )}
      </div>
    </main>
  );
}