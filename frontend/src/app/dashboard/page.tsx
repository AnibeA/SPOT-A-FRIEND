'use client';

import { useSearchParams } from 'next/navigation';
import { useEffect, useState } from 'react';

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
          topArtists: artistsData.top_artists || []
        });
      } catch (err) {
        console.error("Error fetching user data:", err);
      }
    };

    fetchUserData();
  }, [spotifyId]);

  return (
    <div className="p-8">
      <h1 className="text-3xl font-bold mb-6">Welcome to your Dashboard</h1>

      <div className="mb-8">
        <h2 className="text-2xl font-semibold">🎵 Top Genres</h2>
        <ul className="list-disc list-inside mt-2">
          {userData.topGenres.map((genre, index) => (
            <li key={index}>{genre}</li>
          ))}
        </ul>
      </div>

      <div>
        <h2 className="text-2xl font-semibold">👨‍🎤 Top Artists</h2>
        <ul className="list-disc list-inside mt-2">
          {userData.topArtists.map((artist, index) => (
            <li key={index}>{artist}</li>
          ))}
        </ul>
      </div>
    </div>
  );
}
