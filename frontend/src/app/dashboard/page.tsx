'use client';

import { useSearchParams } from 'next/navigation';
import { useEffect, useState } from 'react';
import LogoutButton from '../components/LogoutButton';

export default function DashboardPage() {
  const searchParams = useSearchParams();
  const spotifyId = searchParams.get('spotify_id');

  const [userData, setUserData] = useState({
    topGenres: [],
    topArtists: []
  });

  const [showInviteOptions, setShowInviteOptions] = useState(false);
  const inviteLink = `http://localhost:3000/invite?inviter_id=${spotifyId}`;


  const toggleInvitePopup = () => setShowInviteOptions(prev => !prev);

  const copyLink = async () => {
    try {
      await navigator.clipboard.writeText(inviteLink);
      alert("Invite link copied to clipboard!");
    } catch (err) {
      console.error("Failed to copy invite link", err);
    }
  };

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
          topArtists: artistsData.items || []
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

      <div className="flex gap-4 mb-6">
        <LogoutButton />
        <button
          onClick={toggleInvitePopup}
          className="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded"
        >
          Invite a Friend
        </button>
      </div>

      {/* 📤 Invite popup options */}
      {showInviteOptions && (
        <div className="bg-gray-800 text-white p-4 rounded shadow-md mb-8 max-w-md">
          <p className="mb-2">Share this invite link:</p>
          <p className="text-sm break-words bg-black p-2 rounded mb-3">{inviteLink}</p>

          <div className="flex flex-col gap-2">
            <button
              onClick={copyLink}
              className="bg-gray-600 hover:bg-gray-700 px-3 py-1 rounded"
            >
              📋 Copy to Clipboard
            </button>

            <a
              href={`mailto:?subject=Join me on Spot-A-Friend&body=Use this link to join: ${inviteLink}`}
              className="text-blue-400 underline"
            >
              📧 Send via Email
            </a>

            <a
              href={`sms:?&body=Hey! Check out this app: ${inviteLink}`}
              className="text-blue-400 underline"
            >
              📱 Send via SMS
            </a>
          </div>
        </div>
      )}

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
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-6 mt-4">
          {userData.topArtists.map((artist, index) => (
            <div key={index} className="bg-white text-black p-4 rounded shadow-md text-center">
              {artist.images && artist.images[0] && (
                <img
                  src={artist.images[0].url}
                  alt={artist.name}
                  className="w-full h-40 object-cover rounded mb-2"
                />
              )}
              <h3 className="text-lg font-semibold">{artist.name}</h3>
              {artist.external_urls?.spotify && (
                <a
                  href={artist.external_urls.spotify}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-blue-600 text-sm underline"
                >
                  View on Spotify
                </a>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
