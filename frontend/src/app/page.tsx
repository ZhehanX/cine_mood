'use client';

import { useState } from 'react';
import axios from 'axios';
import MovieCard from './components/Movie_card';


interface Movie {
  id: number;
  title: string;
  year: string;
  poster_url: string;
  overview: string;
  genres: string[]; 
}

export default function HomePage() {
  const [prompt, setPrompt] = useState('');
  const [movies, setMovies] = useState<Movie[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isMounted, setIsMounted] = useState(false);


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
    <main className="min-h-screen bg-gray-900 text-white p-4 sm:p-8">
      <div className="container mx-auto max-w-6xl text-center">
        <h1 className="text-4xl sm:text-5xl font-bold mb-4">🎬 CineMood</h1>
        <p className="text-lg sm:text-xl text-gray-400 mb-8">¿Qué película te apetece ver hoy?</p>
        
        <form onSubmit={handleSubmit} className="mb-12 max-w-2xl mx-auto">
          <div className="flex items-center gap-x-3">
            <input
              type="text"
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              placeholder="Ej: 'Me siento aventurero y quiero ver algo con mucha acción'"
              className="flex-grow p-4 rounded-lg bg-gray-800 border border-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500 transition"
            />
            <button
              type="submit"
              disabled={isLoading}
              className="px-6 py-4 bg-blue-600 rounded-lg font-semibold hover:bg-blue-700 transition disabled:bg-gray-500 disabled:cursor-not-allowed whitespace-nowrap"
            >
              {isLoading ? 'Buscando...' : 'Encuentra mi película'}
            </button>
          </div>
        </form>

        {error && <p className="text-red-500 text-lg">{error}</p>}

        {movies.length > 0 && (
          <div>
            <h2 className="text-3xl font-bold mb-6">Aquí tienes algunas recomendaciones:</h2>
            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-6">
              {movies.map((movie) => (
                <MovieCard key={movie.id} movie={movie} />
              ))}
            </div>
          </div>
        )}
      </div>
    </main>
  );
}

