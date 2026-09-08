import React, { useState } from "react";
import { uploadTender } from "../api";

const categoryStyles = {
  GST: "bg-green-100 text-green-700 border-green-300",     // processed in Phase 1
  PAN: "bg-gray-100 text-gray-500 border-gray-300",         // detected only, future phase
  MSME: "bg-gray-100 text-gray-500 border-gray-300",
  ECS: "bg-gray-100 text-gray-500 border-gray-300",
};

export default function TenderUpload({ user }) {
  const [file, setFile] = useState(null);
  const [showOverrides, setShowOverrides] = useState(false);
  const [manualTenderId, setManualTenderId] = useState("");
  const [manualTenderTitle, setManualTenderTitle] = useState("");
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleUpload(e) {
    e.preventDefault();
    setError("");
    setResult(null);

    if (!file) {
      setError("Please choose a tender PDF file first.");
      return;
    }

    setLoading(true);
    try {
      const { ok, data } = await uploadTender(file, user.id, manualTenderId, manualTenderTitle);
      if (!ok) {
        setError(data.error || "Upload failed");
      } else {
        setResult(data);
      }
    } catch (err) {
      setError("Could not reach backend. Is Flask running?");
    }
    setLoading(false);
  }

  return (
    <div className="max-w-2xl mx-auto p-6">
      <h1 className="text-2xl font-bold text-gemblue mb-1">Upload Tender</h1>
      <p className="text-gray-500 mb-6">
        Works with any GeM tender PDF — the system reads the tender ID, title,
        ministry, department and required documents straight out of the file.
        Only verified users ({user.role}) can upload.
      </p>

      <form onSubmit={handleUpload} className="bg-white rounded-lg shadow p-6 space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Tender PDF</label>
          <input
            type="file"
            accept="application/pdf"
            onChange={(e) => setFile(e.target.files[0])}
            className="w-full text-sm"
            required
          />
        </div>

        <button
          type="button"
          onClick={() => setShowOverrides(!showOverrides)}
          className="text-xs text-gemblue underline"
        >
          {showOverrides ? "Hide manual override fields" : "Need to override the auto-detected Tender ID/Title?"}
        </button>

        {showOverrides && (
          <div className="space-y-3 border-t pt-3">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Tender ID (optional override)
              </label>
              <input
                value={manualTenderId}
                onChange={(e) => setManualTenderId(e.target.value)}
                placeholder="Leave blank to auto-detect from PDF"
                className="w-full border border-gray-300 rounded-md px-3 py-2"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Tender Title (optional override)
              </label>
              <input
                value={manualTenderTitle}
                onChange={(e) => setManualTenderTitle(e.target.value)}
                placeholder="Leave blank to auto-detect from PDF"
                className="w-full border border-gray-300 rounded-md px-3 py-2"
              />
            </div>
          </div>
        )}

        {error && <p className="text-red-600 text-sm">{error}</p>}

        <button
          type="submit"
          disabled={loading}
          className="bg-gemblue text-white px-4 py-2 rounded-md font-semibold hover:bg-blue-900 disabled:opacity-50"
        >
          {loading ? "Analyzing tender..." : "Upload & Analyze Tender"}
        </button>
      </form>

      {result && (
        <div className="mt-6 bg-white rounded-lg shadow p-5 space-y-4">
          <div>
            <h2 className="font-semibold text-lg text-gray-800 mb-2">Extracted Tender Info</h2>
            <table className="text-sm w-full">
              <tbody>
                <tr>
                  <td className="font-medium pr-4 py-1 text-gray-600">Tender ID</td>
                  <td>
                    {result.tender_id}
                    {result.tender_id_auto_generated && (
                      <span className="ml-2 text-xs text-orange-600">
                        (no GEM number found in PDF — generated automatically)
                      </span>
                    )}
                  </td>
                </tr>
                <tr><td className="font-medium pr-4 py-1 text-gray-600">Title</td><td>{result.tender_title}</td></tr>
                <tr><td className="font-medium pr-4 py-1 text-gray-600">Ministry</td><td>{result.ministry || "-"}</td></tr>
                <tr><td className="font-medium pr-4 py-1 text-gray-600">Department</td><td>{result.department || "-"}</td></tr>
                <tr><td className="font-medium pr-4 py-1 text-gray-600">Bid End Date</td><td>{result.bid_end_date || "-"}</td></tr>
                <tr><td className="font-medium pr-4 py-1 text-gray-600">Extraction method</td><td>{result.extraction_method} ({result.page_count} pages)</td></tr>
                <tr><td className="font-medium pr-4 py-1 text-gray-600">Tender DB ID</td><td className="font-semibold">{result.tender_db_id} <span className="text-xs text-gray-400">(use this on the Bidders page)</span></td></tr>
              </tbody>
            </table>
          </div>

          <div>
            <h3 className="font-semibold text-gray-800 mb-2">Requirements Detected in this Tender</h3>
            <div className="flex flex-wrap gap-2">
              {result.requirements_detected && result.requirements_detected.length > 0 ? (
                result.requirements_detected.map((r) => (
                  <span
                    key={r.category}
                    className={`text-xs px-3 py-1 rounded-full border font-medium ${categoryStyles[r.category] || "bg-gray-100 text-gray-500 border-gray-300"}`}
                  >
                    {r.category}
                    {r.category === "GST" ? " (processed in Phase 1)" : " (detected — future phase)"}
                  </span>
                ))
              ) : (
                <span className="text-sm text-gray-400">No known requirement keywords detected.</span>
              )}
            </div>
            {!result.gst_requirement_detected && (
              <p className="text-sm text-orange-600 mt-2">
                No GST requirement was found in this tender — GST verification won't be applicable here.
              </p>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
