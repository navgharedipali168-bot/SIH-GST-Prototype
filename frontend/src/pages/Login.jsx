import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { loginUser } from "../api";

export default function Login({ setUser }) {
  const [email, setEmail] = useState("officer@gem.gov.in");
  const [password, setPassword] = useState("officer123");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const { ok, data } = await loginUser(email, password);
      if (!ok) {
        setError(data.error || "Login failed");
        setLoading(false);
        return;
      }
      setUser(data.user);
      localStorage.setItem("gst_user", JSON.stringify(data.user));
      navigate("/dashboard");
    } catch (err) {
      setError("Could not reach backend. Is Flask running on port 5000?");
    }
    setLoading(false);
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-gemblue to-blue-900">
      <div className="bg-white rounded-xl shadow-2xl p-8 w-full max-w-sm">
        <h1 className="text-2xl font-bold text-gemblue mb-1">GST Compliance Login</h1>
        <p className="text-sm text-gray-500 mb-6">GeM Bid Compliance Verification - Phase 1</p>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-gemblue"
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-gemblue"
              required
            />
          </div>

          {error && <p className="text-red-600 text-sm">{error}</p>}

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-gemblue text-white py-2 rounded-md font-semibold hover:bg-blue-900 disabled:opacity-50"
          >
            {loading ? "Logging in..." : "Login"}
          </button>
        </form>

        <div className="mt-6 text-xs text-gray-400 border-t pt-3">
          <p className="font-semibold mb-1">Mock accounts:</p>
          <p>officer@gem.gov.in / officer123 (verified)</p>
          <p>admin@gem.gov.in / admin123 (verified)</p>
          <p>guest@example.com / guest123 (NOT verified - upload blocked)</p>
        </div>
      </div>
    </div>
  );
}
