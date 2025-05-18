"use client"; // ✅ Tells Next.js this is a Client Component so we can use useState, event handlers, etc.

import { useState } from "react"; // ✅ Import React's useState for managing form input and API response

// ✅ Function to fetch data from your Flask backend's /compare-users route
async function fetchUserComparison(user1: string, user2: string) {
    try {
        const response = await fetch(`http://127.0.0.1:5000/compare-users?user1=${user1}&user2=${user2}`);
        if (!response.ok) {
            throw new Error("Failed to fetch user comparison data");
        }
        return await response.json(); // Parse the JSON data returned
    } catch (error) {
        console.error("Error fetching user comparison:", error); // Log any error for debugging
        return null;
    }
}

//  Main functional component for comparing Spotify users
export default function UserComparison() {
    //  State variables to track input and data
    const [user1, setUser1] = useState(""); // Spotify ID for user 1
    const [user2, setUser2] = useState(""); // Spotify ID for user 2
    const [data, setData] = useState<any>(null); // API response data
    const [loading, setLoading] = useState(false); // Loading state
    const [error, setError] = useState(""); // Error message

    // ✅ Function to trigger API call and update UI
    const handleCompare = async () => {
        setLoading(true);
        setError(""); // Clear previous error
        const result = await fetchUserComparison(user1, user2); // Call the backend

        if (result) {
            setData(result); // Save result to state
        } else {
            setError("Failed to load data. Check user IDs.");
        }

        setLoading(false); // Reset loading state
    };

    return (
        <div className="p-6 max-w-2xl mx-auto bg-white rounded-lg shadow">
            {/* 🔹 Title */}
            <h2 className="text-2xl font-bold mb-4">Compare Spotify Users</h2>

            {/* 🔹 Input for User 1 */}
            <input
                type="text"
                placeholder="Enter User 1 Spotify ID"
                value={user1}
                onChange={(e) => setUser1(e.target.value)}
                className="border p-2 rounded w-full mb-2"
            />

            {/* 🔹 Input for User 2 */}
            <input
                type="text"
                placeholder="Enter User 2 Spotify ID"
                value={user2}
                onChange={(e) => setUser2(e.target.value)}
                className="border p-2 rounded w-full mb-2"
            />

            {/* 🔹 Compare button */}
            <button
                onClick={handleCompare}
                className="bg-blue-500 text-white px-4 py-2 rounded"
                disabled={loading}
            >
                {loading ? "Comparing..." : "Compare"}
            </button>

            {/* 🔹 Error message if something goes wrong */}
            {error && <p className="text-red-500 mt-2">{error}</p>}

            {/* 🔹 Display comparison results if data exists */}
            {data && (
                <div className="mt-4">
                    <h3 className="text-lg font-semibold">Similarity Score:</h3>
                    <p>{(data.cosine_similarity * 100).toFixed(2)}%</p>

                    <h3 className="text-lg font-semibold mt-4">Recommended Artists:</h3>
                    <p><strong>User 1:</strong> {data.user1_recommended_artists.join(", ")}</p>
                    <p><strong>User 2:</strong> {data.user2_recommended_artists.join(", ")}</p>
                </div>
            )}
        </div>
    );
}
