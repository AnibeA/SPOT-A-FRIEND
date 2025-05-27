'use client';

import { useEffect, useState } from 'react';
import { useSearchParams } from 'next/navigation';

interface Artist {
  name: string;
  genres: string[];
  images: { url: string }[];
  external_urls: { spotify: string };
}

interface ComparisonResult {
  merged_artists: Artist[];
  merged_genres: string[];
  merged_sub_genres: string[];
  user1_recommended_artists: string[];
  user2_recommended_artists: string[];
  user1_vector: number[];
  user2_vector: number[];
  all_genres_list: string[];
  cosine_similarity: number;
}

export default function UserComparison() {
  const searchParams = useSearchParams();
  const user1 = searchParams.get('user1');
  const user2 = searchParams.get('user2');

  const [comparison, setComparison] = useState<ComparisonResult | null>(null);

  useEffect(() => {
    const fetchComparison = async () => {
      if (!user1 || !user2) return;

      try {
        const res = await fetch(`http://127.0.0.1:5000/compare-users?user1=${user1}&user2=${user2}`);
        const data = await res.json();
        setComparison(data);
      } catch (err) {
        console.error('Error fetching comparison:', err);
      }
    };

    fetchComparison();
  }, [user1, user2]);

  const inviteLink = user1
    ? `http://127.0.0.1:5000/login?inviter_id=${user1}`
    : '';

  return (
    <div className="p-8">
      <h1 className="text-3xl font-bold mb-6">🎧 Compare Users</h1>

      {user1 && (
        <div className="mb-8">
          <h2 className="text-xl font-semibold">Invite another user</h2>
          <p className="text-sm text-gray-600 mb-2">
            Share this link with someone else to compare Spotify data:
          </p>

          <div className="flex items-center gap-2">
            <input
              type="text"
              readOnly
              value={inviteLink}
              className="w-full border rounded px-3 py-2 bg-gray-100 text-sm"
            />
            <button
              onClick={() => {
                navigator.clipboard.writeText(inviteLink);
                alert('Link copied to clipboard!');
              }}
              className="px-3 py-2 bg-blue-500 text-white text-sm rounded hover:bg-blue-600"
            >
              Copy
            </button>
          </div>

          <div className="flex gap-4 mt-3">
            <a
              href={`https://wa.me/?text=${encodeURIComponent(inviteLink)}`}
              target="_blank"
              rel="noopener noreferrer"
              className="text-green-600 underline"
            >
              Share via WhatsApp
            </a>
            <a
              href={`mailto:?subject=Join me on Spot-a-Friend&body=${encodeURIComponent(inviteLink)}`}
              className="text-blue-700 underline"
            >
              Share via Email
            </a>
          </div>
        </div>
      )}

      {comparison ? (
        <>
          <div className="mb-6">
            <h2 className="text-xl font-semibold">🔁 Shared Genres</h2>
            <p>{comparison.merged_genres.join(', ')}</p>
          </div>

          <div className="mb-6">
            <h2 className="text-xl font-semibold">🧠 Cosine Similarity Score</h2>
            <p className="text-lg font-bold">{comparison.cosine_similarity.toFixed(2)}</p>
          </div>

          <div className="mb-6">
            <h2 className="text-xl font-semibold">🎯 Recommended for You</h2>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <h3 className="font-semibold">User 1 Recommendations</h3>
                <ul className="list-disc list-inside">
                  {comparison.user1_recommended_artists.map((artist, index) => (
                    <li key={index}>{artist}</li>
                  ))}
                </ul>
              </div>
              <div>
                <h3 className="font-semibold">User 2 Recommendations</h3>
                <ul className="list-disc list-inside">
                  {comparison.user2_recommended_artists.map((artist, index) => (
                    <li key={index}>{artist}</li>
                  ))}
                </ul>
              </div>
            </div>
          </div>
        </>
      ) : (
        <p>Loading comparison data...</p>
      )}
    </div>
  );
}
