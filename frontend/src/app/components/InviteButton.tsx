'use client';

import { useState } from 'react';

export default function InviteButton({ spotifyId }: { spotifyId: string }) {
  const [showModal, setShowModal] = useState(false);
  const inviteLink = `http://localhost:3000/invite?inviter_id=${spotifyId}`;

  const copyToClipboard = async () => {
    try {
      await navigator.clipboard.writeText(inviteLink);
      alert('Invite link copied!');
    } catch (err) {
      console.error('Failed to copy:', err);
    }
  };

  return (
    <>
      <button
        className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 mb-4"
        onClick={() => setShowModal(true)}
      >
        Invite a Friend
      </button>

      {showModal && (
        <div className="fixed inset-0 flex items-center justify-center bg-black bg-opacity-40 z-50">
          <div className="bg-white rounded-lg p-6 shadow-lg max-w-md w-full">
            <h2 className="text-xl font-semibold mb-4">Share Your Invite Link</h2>
            <p className="mb-2 text-sm break-all">{inviteLink}</p>

            <div className="space-y-3">
              <button
                onClick={copyToClipboard}
                className="w-full bg-gray-200 px-3 py-2 rounded hover:bg-gray-300"
              >
                📋 Copy to Clipboard
              </button>

              <a
                href={`mailto:?subject=Join me on Spot-A-Friend&body=Check this out: ${inviteLink}`}
                className="block w-full bg-green-200 text-center px-3 py-2 rounded hover:bg-green-300"
              >
                📧 Send via Email
              </a>

              <a
                href={`sms:?body=Join me on Spot-A-Friend: ${inviteLink}`}
                className="block w-full bg-yellow-200 text-center px-3 py-2 rounded hover:bg-yellow-300"
              >
                📱 Send via SMS
              </a>
            </div>

            <button
              onClick={() => setShowModal(false)}
              className="mt-4 text-sm text-gray-500 underline"
            >
              Close
            </button>
          </div>
        </div>
      )}
    </>
  );
}
