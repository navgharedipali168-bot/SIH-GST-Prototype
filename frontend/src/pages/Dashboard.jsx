import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { listTenders, getComplianceDashboard } from "../api";

export default function Dashboard() {
  const [tenders, setTenders] = useState([]);
  const [summaries, setSummaries] = useState({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      const list = await listTenders();
      setTenders(list);

      const summaryMap = {};
      for (const t of list) {
        try {
          const dash = await getComplianceDashboard(t.id);
          summaryMap[t.id] = dash;
        } catch {
          // ignore individual failures
        }
      }
      setSummaries(summaryMap);
      setLoading(false);
    }
    load();
  }, []);

  return (
    <div className="max-w-6xl mx-auto p-6">
      <h1 className="text-2xl font-bold text-gemblue mb-1">Tender Dashboard</h1>
      <p className="text-gray-500 mb-6">Overview of all tenders and their GST compliance status</p>

      {loading && <p className="text-gray-400">Loading...</p>}

      {!loading && tenders.length === 0 && (
        <div className="bg-white rounded-lg shadow p-8 text-center text-gray-500">
          No tenders yet.{" "}
          <Link to="/tender-upload" className="text-gemblue font-semibold underline">
            Upload your first tender
          </Link>
        </div>
      )}

      <div className="grid gap-4">
        {tenders.map((t) => {
          const s = summaries[t.id];
          return (
            <div key={t.id} className="bg-white rounded-lg shadow p-5">
              <div className="flex justify-between items-start">
                <div>
                  <h2 className="font-semibold text-lg text-gray-800">{t.tender_title || "Untitled Tender"}</h2>
                  <p className="text-sm text-gray-500">Tender ID: {t.tender_id}</p>
                  <p className="text-sm text-gray-500">GST Requirement: Detected</p>
                </div>
                <Link
                  to="/comparative"
                  className="text-sm bg-gemblue text-white px-3 py-1.5 rounded-md hover:bg-blue-900"
                >
                  View Comparative Dashboard
                </Link>
              </div>

              {s && (
                <div className="grid grid-cols-4 gap-3 mt-4">
                  <StatBox label="Bidders" value={s.total_bidders} color="bg-gray-100 text-gray-700" />
                  <StatBox label="PASS" value={s.pass_count} color="bg-green-100 text-green-700" />
                  <StatBox label="FAIL" value={s.fail_count} color="bg-red-100 text-red-700" />
                  <StatBox label="REVIEW" value={s.review_count} color="bg-yellow-100 text-yellow-700" />
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}

function StatBox({ label, value, color }) {
  return (
    <div className={`rounded-md p-3 text-center ${color}`}>
      <p className="text-2xl font-bold">{value ?? 0}</p>
      <p className="text-xs font-medium">{label}</p>
    </div>
  );
}
