interface Movie {
  id: number;
  title: string;
  year: string;
  poster_url: string;
  overview: string;
  genres: string[];
}

interface MovieCardProps {
  movie: Movie;
}

const MovieCard = ({ movie }: MovieCardProps) => {
  const posterSrc = movie.poster_url || 'https://via.placeholder.com/500x750.png?text=No+Image';

  return (
    <div className="bg-gray-800 rounded-lg overflow-hidden shadow-lg flex flex-col h-full transform hover:scale-105 transition-transform duration-300">
      <div className="relative w-full" style={{ paddingBottom: '150%' }}>
        <img
          src={posterSrc}
          alt={`Póster de ${movie.title || 'película'}`}
          className="absolute top-0 left-0 w-full h-full object-cover"
          loading="lazy"
        />
      </div>
      <div className="p-4 flex flex-col flex-grow">
        <h3 className="text-xl font-bold text-white truncate mb-1">{movie.title}</h3>
        <p className="text-gray-400 mb-2 text-sm">{movie.year}</p>
        <p className="text-gray-300 text-sm overflow-hidden flex-grow" style={{ display: '-webkit-box', WebkitLineClamp: 3, WebkitBoxOrient: 'vertical' }}>
          {movie.overview}
        </p>
        
        <div className="mt-3 pt-3 border-t border-gray-700 flex flex-wrap gap-2">
          {movie.genres && movie.genres.map((genre) => (
            <span key={genre} className="bg-gray-700 text-blue-300 text-xs font-semibold px-2 py-1 rounded-full">
              {genre}
            </span>
          ))}
        </div>
      </div>
    </div>
  );
};

export default MovieCard;

