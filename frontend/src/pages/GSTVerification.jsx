import React, { useState } from "react";
import { verifyGst } from "../api";

const resultStyles = {
  PASS: "bg-green-100 text-green-700 border-green-400",
  FAIL: "bg-red-100 text-red-700 border-red-400",
  REVIEW: "bg-yellow-100 text-yellow-700 border-yellow-400",
};

export default function GSTVerification() {
  const [documentId, setDocumentId] = useState("1");
  const [bidderId, setBidderId] = useState("1");
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleVerify(e) {
    e.preventDefault();
    setError("");
    setResult(null);
    setLoading(true);
    try {
      const { ok, data } = await verifyGst(documentId, bidderId);
      if (!ok) setError(data.error || "Verification failed");
      else setResult(data);
    } catch (err) {
      setError("Could not reach backend.");
    }
    setLoading(false);
  }

  return (
    <div className="max-w-2xl mx-auto p-6">
      <h1 className="text-2xl font-bold text-gemblue mb-1">GST Verification</h1>
      <p className="text-gray-500 mb-6">
        Run the verification engine against a bidder's uploaded GST certificate.
      </p>

      <form onSubmit={handleVerify} className="bg-white rounded-lg shadow p-6 space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Document ID</label>
          <input
            value={documentId}
            onChange={(e) => setDocumentId(e.target.value)}
            className="w-full border border-gray-300 rounded-md px-3 py-2"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Bidder ID</label>
          <input
            value={bidderId}
            onChange={(e) => setBidderId(e.target.value)}
            className="w-full border border-gray-300 rounded-md px-3 py-2"
          />
        </div>

        {error && <p className="text-red-600 text-sm">{error}</p>}

        <button
          disabled={loading}
          className="bg-gemblue text-white px-4 py-2 rounded-md font-semibold hover:bg-blue-900 disabled:opacity-50"
        >
          {loading ? "Verifying..." : "Run GST Verification"}
        </button>
      </form>

      {result && (
        <div className={`mt-6 rounded-lg shadow p-5 border-l-4 ${resultStyles[result.result] || ""}`}>
          <h2 className="font-bold text-xl mb-2">{result.result}</h2>
          <table className="text-sm w-full">
            <tbody>
              <tr><td className="font-medium pr-4 py-1">Bidder</td><td>{result.bidder_name}</td></tr>
              <tr><td className="font-medium pr-4 py-1">GSTIN</td><td>{result.extracted_gstin || "Not found"}</td></tr>
              <tr><td className="font-medium pr-4 py-1">Company Name (DB)</td><td>{result.matched_company_name || "-"}</td></tr>
              <tr><td className="font-medium pr-4 py-1">GST Status</td><td>{result.gst_status || "-"}</td></tr>
              <tr><td className="font-medium pr-4 py-1 align-top">Reason</td><td>{result.reason}</td></tr>
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
