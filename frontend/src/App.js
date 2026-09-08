import React, { useEffect, useState } from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";

import Navbar from "./components/Navbar";
import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";
import TenderUpload from "./pages/TenderUpload";
import BidderManagement from "./pages/BidderManagement";
import GSTVerification from "./pages/GSTVerification";
import ComparativeDashboard from "./pages/ComparativeDashboard";

function PrivateRoute({ user, children }) {
  if (!user) return <Navigate to="/login" replace />;
  return children;
}

export default function App() {
  const [user, setUser] = useState(null);

  useEffect(() => {
    const stored = localStorage.getItem("gst_user");
    if (stored) setUser(JSON.parse(stored));
  }, []);

  return (
    <BrowserRouter>
      <Navbar user={user} setUser={setUser} />
      <Routes>
        <Route path="/login" element={<Login setUser={setUser} />} />
        <Route
          path="/dashboard"
          element={
            <PrivateRoute user={user}>
              <Dashboard />
            </PrivateRoute>
          }
        />
        <Route
          path="/tender-upload"
          element={
            <PrivateRoute user={user}>
              <TenderUpload user={user} />
            </PrivateRoute>
          }
        />
        <Route
          path="/bidders"
          element={
            <PrivateRoute user={user}>
              <BidderManagement user={user} />
            </PrivateRoute>
          }
        />
        <Route
          path="/gst-verification"
          element={
            <PrivateRoute user={user}>
              <GSTVerification />
            </PrivateRoute>
          }
        />
        <Route
          path="/comparative"
          element={
            <PrivateRoute user={user}>
              <ComparativeDashboard />
            </PrivateRoute>
          }
        />
        <Route path="*" element={<Navigate to={user ? "/dashboard" : "/login"} replace />} />
      </Routes>
    </BrowserRouter>
  );
}
