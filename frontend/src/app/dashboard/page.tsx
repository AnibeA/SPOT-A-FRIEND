'use client';

import { useSearchParams } from 'next/navigation';
import { useEffect, useState } from 'react';
import LogoutButton from '@/components/LogoutButton';

export default function DashboardPage() {
  const searchParams = useSearchParams();
  const spotifyId = searchParams.get('spotify_id');

  const [userData, setUserData] = useState({
    topGenres: [],
    topArtists: []
  });

  useEffect(() => {
    const fetchUserData = async () => {
      if (!spotifyId) return;

      try {
        const genresRes = await fetch(`http://127.0.0.1:5000/top-genres?spotify_id=${spotifyId}`);
        const artistsRes = await fetch(`http://127.0.0.1:5000/top-artists?spotify_id=${spotifyId}`);
        
        const genresData = await genresRes.json();
        const artistsData = await artistsRes.json();

        setUserData({
          topGenres: genresData.top_genres || [],
          topArtists: artistsData.items || [] // ✅ FIX: Pull actual artist list from "items"
        });
      } catch (err) {
        console.error("Error fetching user data:", err);
      }
    };

    fetchUserData();
  }, [spotifyId]);

  return (
    <div className="p-8 bg-black text-white min-h-screen">
      <h1 className="text-3xl font-bold mb-6">Welcome to your Dashboard</h1>

      <div className="mb-10">
        <h2 className="text-2xl font-semibold mb-2">🎵 Top Genres</h2>
        <ul className="list-disc list-inside space-y-1">
          {userData.topGenres.map((genre, index) => (
            <li key={index}>{genre}</li>
          ))}
        </ul>
      </div>

      <div>
        <h2 className="text-2xl font-semibold mb-4">👨‍🎤 Top Artists</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
          {userData.topArtists.map((artist) => (
            <div key={artist.id} className="bg-white text-black rounded-lg p-4 shadow-lg text-center">
              <img
                src={artist.images?.[0]?.url || '/fallback-image.png'}
                alt={artist.name}
                className="w-full h-40 object-cover rounded"
              />
              <h3 className="mt-3 text-lg font-semibold">{artist.name}</h3>
              <a
                href={artist.external_urls.spotify}
                target="_blank"
                rel="noopener noreferrer"
                className="text-blue-500 text-sm block mt-1"
              >
                View on Spotify
              </a>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
