'use client';

export default function LandingPage() {
  return (
    <div className="min-h-screen flex flex-col justify-center items-center bg-gradient-to-br from-green-700 to-black-500 text-white px-6">
      <h1 className="text-5xl font-bold mb-4"> Spot-A-Friend</h1>
      <p className="text-xl text-center max-w-xl mb-8">
        Discover new music and connect with friends through your Spotify listening habits.
        Compare genres, artists, and find your musical match!
      </p>

      {/* ✅ Replace with actual Flask login URL */}
      <a
        href="http://localhost:5000/login"
        className="bg-black text-green-700 px-6 py-3 rounded-lg shadow-lg font-semibold hover:bg-green-200 transition"
      >
        Get Started
      </a>
    </div>
  );
}
