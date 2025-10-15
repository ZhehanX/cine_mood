import Image from 'next/image';

// Definimos la 'forma' de los datos de una película
interface Movie {
  Title: string;
  Year: string;
  imdbID: string;
  Type: string;
  Poster: string;
}

interface MovieCardProps {
  movie: Movie;
}

const MovieCard = ({ movie }: MovieCardProps) => {
  // OMDb a veces devuelve 'N/A' como póster
  const posterSrc = movie.Poster !== 'N/A' ? movie.Poster : 'https://via.placeholder.com/300x450.png?text=No+Image';

  return (
    <div className="bg-gray-800 rounded-lg overflow-hidden shadow-lg transform hover:scale-105 transition-transform duration-300">
      <div className="relative w-full h-96">
        <Image
          src={posterSrc}
          alt={`Póster de ${movie.Title}`}
          layout="fill"
          objectFit="cover"
        />
      </div>
      <div className="p-4">
        <h3 className="text-xl font-bold text-white truncate">{movie.Title}</h3>
        <p className="text-gray-400">{movie.Year}</p>
      </div>
    </div>
  );
};

export default MovieCard;