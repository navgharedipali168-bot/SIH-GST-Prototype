import React from "react";
import { Link, useNavigate } from "react-router-dom";

export default function Navbar({ user, setUser }) {
  const navigate = useNavigate();

  function handleLogout() {
    setUser(null);
    localStorage.removeItem("gst_user");
    navigate("/login");
  }

  if (!user) return null;

  const linkClass =
    "px-3 py-2 rounded-md text-sm font-medium text-white hover:bg-gemblue/70";

  return (
    <nav className="bg-gemblue shadow-md">
      <div className="max-w-6xl mx-auto px-4 flex items-center justify-between h-14">
        <div className="flex items-center gap-2">
          <span className="text-white font-bold text-lg">GeM GST Compliance</span>
          <span className="text-xs bg-yellow-400 text-black px-2 py-0.5 rounded-full font-semibold">
            Phase 1 Prototype
          </span>
        </div>
        <div className="flex items-center gap-1">
          <Link to="/dashboard" className={linkClass}>Dashboard</Link>
          <Link to="/tender-upload" className={linkClass}>Upload Tender</Link>
          <Link to="/bidders" className={linkClass}>Bidders</Link>
          <Link to="/gst-verification" className={linkClass}>GST Verification</Link>
          <Link to="/comparative" className={linkClass}>Comparative View</Link>
          <span className="text-white text-sm ml-3">{user.name} ({user.role})</span>
          <button
            onClick={handleLogout}
            className="ml-2 px-3 py-1.5 bg-red-500 hover:bg-red-600 text-white text-sm rounded-md"
          >
            Logout
          </button>
        </div>
      </div>
    </nav>
  );
}
