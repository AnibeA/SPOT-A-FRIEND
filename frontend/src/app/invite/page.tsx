'use client';

import { useSearchParams } from 'next/navigation';
import { useEffect } from 'react';

export default function InvitePage() {
  const searchParams = useSearchParams();
  const inviterId = searchParams.get('inviter_id');

  useEffect(() => {
    if (!inviterId) return;

    const redirectToSpotifyLogin = async () => {
      try {
        // Store inviter_id temporarily in sessionStorage
        sessionStorage.setItem('inviter_id', inviterId);

        // Redirect user to backend Spotify login
        window.location.href = `http://127.0.0.1:5000/login?inviter_id=${inviterId}`;
      } catch (error) {
        console.error('Error redirecting to Spotify login:', error);
      }
    };

    redirectToSpotifyLogin();
  }, [inviterId]);

  return (
    <div className="flex flex-col items-center justify-center h-screen text-center">
      <h1 className="text-2xl font-semibold">Connecting to Spotify...</h1>
      <p className="mt-2">Please wait while we redirect you to login.</p>
    </div>
  );
}
