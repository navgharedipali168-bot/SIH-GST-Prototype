import React, { useState } from "react";
import { addBidder, listBidders, uploadBidderDocument } from "../api";

export default function BidderManagement({ user }) {
  const [tenderDbId, setTenderDbId] = useState("1");
  const [bidderName, setBidderName] = useState("");
  const [bidders, setBidders] = useState([]);
  const [message, setMessage] = useState("");
  const [uploadingFor, setUploadingFor] = useState(null);
  const [docFile, setDocFile] = useState(null);

  async function loadBidders() {
    const data = await listBidders(tenderDbId);
    setBidders(data);
  }

  async function handleAddBidder(e) {
    e.preventDefault();
    setMessage("");
    if (!bidderName.trim()) return;
    const { ok, data } = await addBidder(tenderDbId, bidderName, user.id);
    if (ok) {
      setMessage(`Bidder "${bidderName}" added (id: ${data.bidder_id})`);
      setBidderName("");
      loadBidders();
    } else {
      setMessage(data.error || "Failed to add bidder");
    }
  }

  async function handleDocUpload(bidderId) {
    if (!docFile) {
      setMessage("Choose a GST certificate PDF first.");
      return;
    }
    const { ok, data } = await uploadBidderDocument(bidderId, docFile);
    if (ok) {
      setMessage(
        `Document uploaded for bidder ${bidderId} (document_id: ${data.document_id}). ` +
        `Now go to "GST Verification" page and run verification with this document_id.`
      );
      setUploadingFor(null);
      setDocFile(null);
    } else {
      setMessage(data.error || "Upload failed");
    }
  }

  return (
    <div className="max-w-4xl mx-auto p-6">
      <h1 className="text-2xl font-bold text-gemblue mb-1">Bidder Management</h1>
      <p className="text-gray-500 mb-6">Add bidders to a tender and upload their GST certificates.</p>

      <div className="bg-white rounded-lg shadow p-5 mb-6">
        <label className="block text-sm font-medium text-gray-700 mb-1">Tender DB ID</label>
        <div className="flex gap-2">
          <input
            value={tenderDbId}
            onChange={(e) => setTenderDbId(e.target.value)}
            className="border border-gray-300 rounded-md px-3 py-2 w-32"
          />
          <button
            onClick={loadBidders}
            className="bg-gray-700 text-white px-4 py-2 rounded-md text-sm hover:bg-gray-800"
          >
            Load Bidders
          </button>
        </div>
      </div>

      <form onSubmit={handleAddBidder} className="bg-white rounded-lg shadow p-5 mb-6 flex gap-2">
        <input
          value={bidderName}
          onChange={(e) => setBidderName(e.target.value)}
          placeholder="Bidder company name (e.g. ABC Technologies)"
          className="flex-1 border border-gray-300 rounded-md px-3 py-2"
        />
        <button className="bg-gemblue text-white px-4 py-2 rounded-md font-semibold hover:bg-blue-900">
          Add Bidder
        </button>
      </form>

      {message && <p className="text-sm text-blue-700 bg-blue-50 rounded-md p-3 mb-4">{message}</p>}

      <div className="grid gap-3">
        {bidders.map((b) => (
          <div key={b.id} className="bg-white rounded-lg shadow p-4">
            <div className="flex justify-between items-center">
              <div>
                <p className="font-semibold text-gray-800">{b.bidder_name}</p>
                <p className="text-xs text-gray-400">Bidder ID: {b.id}</p>
              </div>
              {uploadingFor === b.id ? (
                <div className="flex items-center gap-2">
                  <input
                    type="file"
                    accept="application/pdf"
                    onChange={(e) => setDocFile(e.target.files[0])}
                    className="text-xs"
                  />
                  <button
                    onClick={() => handleDocUpload(b.id)}
                    className="bg-green-600 text-white px-3 py-1.5 rounded-md text-sm hover:bg-green-700"
                  >
                    Submit
                  </button>
                </div>
              ) : (
                <button
                  onClick={() => setUploadingFor(b.id)}
                  className="bg-gemblue text-white px-3 py-1.5 rounded-md text-sm hover:bg-blue-900"
                >
                  Upload GST Certificate
                </button>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
