// Central place for the backend base URL.
// Change this if your Flask server runs on a different host/port.
export const API_BASE = "http://localhost:5000/api";

export async function loginUser(email, password) {
  const res = await fetch(`${API_BASE}/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });
  return { ok: res.ok, data: await res.json() };
}

export async function listTenders() {
  const res = await fetch(`${API_BASE}/tenders`);
  return res.json();
}

export async function getTender(tenderDbId) {
  const res = await fetch(`${API_BASE}/tenders/${tenderDbId}`);
  return res.json();
}

// tenderId / tenderTitle are OPTIONAL manual overrides now -- the backend
// auto-extracts both straight from the PDF. Pass empty strings ("") to
// let auto-extraction do all the work.
export async function uploadTender(file, uploadedBy, tenderId = "", tenderTitle = "") {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("uploaded_by", uploadedBy);
  if (tenderId) formData.append("tender_id", tenderId);
  if (tenderTitle) formData.append("tender_title", tenderTitle);

  const res = await fetch(`${API_BASE}/tenders/upload`, {
    method: "POST",
    body: formData,
  });
  return { ok: res.ok, data: await res.json() };
}

export async function addBidder(tenderDbId, bidderName, addedBy) {
  const res = await fetch(`${API_BASE}/bidders`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      tender_db_id: tenderDbId,
      bidder_name: bidderName,
      added_by: addedBy,
    }),
  });
  return { ok: res.ok, data: await res.json() };
}

export async function listBidders(tenderDbId) {
  const res = await fetch(`${API_BASE}/bidders/${tenderDbId}`);
  return res.json();
}

export async function uploadBidderDocument(bidderId, file) {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("document_type", "GST Certificate");

  const res = await fetch(`${API_BASE}/bidders/${bidderId}/documents`, {
    method: "POST",
    body: formData,
  });
  return { ok: res.ok, data: await res.json() };
}

export async function verifyGst(documentId, bidderId) {
  const res = await fetch(`${API_BASE}/verify-gst`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ document_id: documentId, bidder_id: bidderId }),
  });
  return { ok: res.ok, data: await res.json() };
}

export async function getComplianceDashboard(tenderDbId) {
  const res = await fetch(`${API_BASE}/tenders/${tenderDbId}/compliance`);
  return res.json();
}
