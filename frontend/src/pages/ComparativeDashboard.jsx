import React, { useState } from "react";
import { getComplianceDashboard } from "../api";

const resultBadge = {
  PASS: "bg-green-100 text-green-700",
  FAIL: "bg-red-100 text-red-700",
  REVIEW: "bg-yellow-100 text-yellow-700",
  PENDING: "bg-gray-100 text-gray-600",
};

const riskBadge = {
  Low: "bg-green-50 text-green-600",
  Medium: "bg-yellow-50 text-yellow-600",
  High: "bg-red-50 text-red-600",
};

export default function ComparativeDashboard() {
  const [tenderDbId, setTenderDbId] = useState("1");
  const [dashboard, setDashboard] = useState(null);
  const [error, setError] = useState("");

  async function loadDashboard() {
    setError("");
    try {
      const data = await getComplianceDashboard(tenderDbId);
      setDashboard(data);
    } catch (err) {
      setError("Could not load dashboard.");
    }
  }

  return (
    <div className="max-w-5xl mx-auto p-6">
      <h1 className="text-2xl font-bold text-gemblue mb-1">Comparative Bidder Dashboard</h1>
      <p className="text-gray-500 mb-6">Side-by-side GST compliance comparison across all bidders.</p>

      <div className="bg-white rounded-lg shadow p-5 mb-6 flex gap-2 items-end">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Tender DB ID</label>
          <input
            value={tenderDbId}
            onChange={(e) => setTenderDbId(e.target.value)}
            className="border border-gray-300 rounded-md px-3 py-2 w-32"
          />
        </div>
        <button
          onClick={loadDashboard}
          className="bg-gemblue text-white px-4 py-2 rounded-md font-semibold hover:bg-blue-900"
        >
          Load Dashboard
        </button>
      </div>

      {error && <p className="text-red-600 text-sm mb-4">{error}</p>}

      {dashboard && (
        <>
          <div className="grid grid-cols-4 gap-3 mb-6">
            <SummaryBox label="Total Bidders" value={dashboard.total_bidders} color="bg-gray-100 text-gray-700" />
            <SummaryBox label="PASS" value={dashboard.pass_count} color="bg-green-100 text-green-700" />
            <SummaryBox label="FAIL" value={dashboard.fail_count} color="bg-red-100 text-red-700" />
            <SummaryBox label="REVIEW" value={dashboard.review_count} color="bg-yellow-100 text-yellow-700" />
          </div>

          <div className="bg-white rounded-lg shadow overflow-hidden">
            <table className="w-full text-sm">
              <thead className="bg-gray-50 text-gray-600 uppercase text-xs">
                <tr>
                  <th className="text-left px-4 py-3">Bidder</th>
                  <th className="text-left px-4 py-3">GSTIN</th>
                  <th className="text-left px-4 py-3">GST Status</th>
                  <th className="text-left px-4 py-3">Result</th>
                  <th className="text-left px-4 py-3">Risk</th>
                  <th className="text-left px-4 py-3">Reason</th>
                </tr>
              </thead>
              <tbody>
                {dashboard.bidders.map((b) => (
                  <tr key={b.bidder_id} className="border-t">
                    <td className="px-4 py-3 font-medium text-gray-800">{b.bidder_name}</td>
                    <td className="px-4 py-3 text-gray-600">{b.gstin || "-"}</td>
                    <td className="px-4 py-3 text-gray-600">{b.gst_status}</td>
                    <td className="px-4 py-3">
                      <span className={`px-2 py-1 rounded-full text-xs font-semibold ${resultBadge[b.result]}`}>
                        {b.result}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      <span className={`px-2 py-1 rounded-full text-xs font-semibold ${riskBadge[b.risk]}`}>
                        {b.risk}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-gray-500 text-xs max-w-xs">{b.reason}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}
    </div>
  );
}

function SummaryBox({ label, value, color }) {
  return (
    <div className={`rounded-md p-4 text-center ${color}`}>
      <p className="text-3xl font-bold">{value ?? 0}</p>
      <p className="text-xs font-medium mt-1">{label}</p>
    </div>
  );
}
