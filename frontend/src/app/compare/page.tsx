'use client';

import { useSearchParams } from 'next/navigation';
import { useEffect, useState } from 'react';

export default function ComparePage() {
  const searchParams = useSearchParams();
  const user1 = searchParams.get('user1');
  const user2 = searchParams.get('user2');

  const [comparisonData, setComparisonData] = useState<any>(null);

  useEffect(() => {
    const fetchComparison = async () => {
      if (!user1 || !user2) return;

      try {
        const res = await fetch(`http://127.0.0.1:5000/compare-users?user1=${user1}&user2=${user2}`);
        const data = await res.json();
        setComparisonData(data);
      } catch (err) {
        console.error('Failed to fetch comparison:', err);
      }
    };

    fetchComparison();
  }, [user1, user2]);

  const getFriendshipLabel = (percentage: number) => {
    if (percentage >= 86) return "👯 Best Friends";
    if (percentage >= 71) return "🤝 Close Friends";
    if (percentage >= 51) return "😊 Friends";
    if (percentage >= 31) return "😐 Acquaintances";
    return "👿 Enemies";
  };

  if (!comparisonData) {
    return (
      <div className="p-8">
        <h1 className="text-2xl font-semibold">Comparing users...</h1>
        <p className="mt-2">Please wait while we fetch the data.</p>
      </div>
    );
  }

  const similarityPercentage = Math.round((comparisonData.cosine_similarity || 0) * 100);
  const label = getFriendshipLabel(similarityPercentage);

  const renderArtists = (artists: any[]) =>
    artists.map((artist: any, index: number) => {
      if (typeof artist === 'string') {
        return <li key={index}>{artist}</li>;
      }

      return (
        <li key={index}>
          <a
            href={artist.external_urls?.spotify || '#'}
            target="_blank"
            rel="noopener noreferrer"
            className="text-blue-600 hover:underline"
          >
            {artist.name}
          </a>
        </li>
      );
    });

  return (
    <div className="p-8">
      <h1 className="text-3xl font-bold mb-6">🎧 User Comparison</h1>

      <div className="mb-6">
        <h2 className="text-2xl font-semibold">🧮 Compatibility</h2>
        <p className="text-xl mt-2">
          You match <span className="font-bold">{similarityPercentage}%</span> – <span>{label}</span>
        </p>
      </div>

      <h2 className="text-2xl font-semibold mt-4">🎵 Shared Genres</h2>
      <ul className="list-disc list-inside mt-2">
        {comparisonData.merged_genres.map((genre: string, index: number) => (
          <li key={index}>{genre}</li>
        ))}
      </ul>

      <h2 className="text-2xl font-semibold mt-6">🎤 User 1 Recommendations</h2>
      <ul className="list-disc list-inside mt-2">
        {renderArtists(comparisonData.user1_recommended_artists)}
      </ul>

      <h2 className="text-2xl font-semibold mt-6">🎤 User 2 Recommendations</h2>
      <ul className="list-disc list-inside mt-2">
        {renderArtists(comparisonData.user2_recommended_artists)}
      </ul>
    </div>
  );
}
