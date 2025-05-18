'use client';

import { useState } from 'react';

export default function LogoutButton() {
  const [message, setMessage] = useState('');

  const handleLogout = async () => {
    try {
      const response = await fetch('http://127.0.0.1:5000/logout', {
        method: 'GET',
        credentials: 'include',
      });

      if (response.ok) {
        setMessage('You have been logged out successfully!');
        setTimeout(() => {
          window.location.href = '/'; // or '/login' or any route
        }, 2000);

      } else {
        setMessage('Logout failed. Please try again.');
      }
    } catch (error) {
      console.error('Logout error:', error);
      setMessage('An error occurred. Please try again later.');
    }
  };

  return (
    <div className="space-y-4">
      <button
        onClick={handleLogout}
        className="bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700"
      >
        Logout
      </button>
      {message && <p className="text-white-700">{message}</p>}
    </div>
  );
}
