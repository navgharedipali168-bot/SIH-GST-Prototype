"""
app.py
-------
Main Flask application. Defines all REST API endpoints for Phase 1
(GST compliance only).

Run with:
    python app.py

Endpoints:
    POST /api/login
    POST /api/tenders/upload
    GET  /api/tenders/<id>
    GET  /api/tenders                     (list all, for dashboard)
    POST /api/bidders
    GET  /api/bidders/<tender_id>         (list bidders for a tender)
    POST /api/bidders/<id>/documents
    POST /api/verify-gst
    GET  /api/tenders/<id>/compliance
"""

import os
import re
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename

from database import get_db_connection
from pdf_processor import process_pdf
from gst_verification import verify_gst
from tender_extractor import extract_tender_info

app = Flask(__name__)
CORS(app)  # allows the React frontend (different port) to call this API

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TENDER_UPLOAD_DIR = os.path.join(BASE_DIR, "uploads", "tenders")
BIDDER_DOC_UPLOAD_DIR = os.path.join(BASE_DIR, "uploads", "bidder_documents")

os.makedirs(TENDER_UPLOAD_DIR, exist_ok=True)
os.makedirs(BIDDER_DOC_UPLOAD_DIR, exist_ok=True)

ALLOWED_EXTENSIONS = {"pdf"}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# ------------------------------------------------------------------
# AUTH
# ------------------------------------------------------------------

@app.route("/api/login", methods=["POST"])
def login():
    """
    Simple mock login. Checks email+password against the users table
    and returns whether the user is_verified.
    NOT secure -- prototype only, no hashing/sessions/JWT.
    """
    data = request.get_json(force=True)
    email = data.get("email", "").strip()
    password = data.get("password", "").strip()

    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "Database connection failed"}), 500

    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT id, name, email, role, is_verified FROM users WHERE email = %s AND password = %s",
        (email, password)
    )
    user = cursor.fetchone()
    cursor.close()
    conn.close()

    if not user:
        return jsonify({"error": "Invalid email or password"}), 401

    if not user["is_verified"]:
        return jsonify({
            "error": "Your account is not verified. You cannot upload tenders or bidder documents.",
            "user": user
        }), 403

    return jsonify({"message": "Login successful", "user": user}), 200


# ------------------------------------------------------------------
# TENDERS
# ------------------------------------------------------------------

@app.route("/api/tenders", methods=["GET"])
def list_tenders():
    """Returns all tenders (for the main dashboard)."""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM tenders ORDER BY created_at DESC")
    tenders = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(tenders), 200


@app.route("/api/tenders/upload", methods=["POST"])
def upload_tender():
    """
    Accepts ANY GeM tender PDF, saves it, extracts its text, and then
    AUTO-EXTRACTS the tender's important info (tender ID, title, ministry,
    department, bid end date, and which requirement categories -- GST,
    PAN, MSME/NSIC, ECS -- are mentioned in it).

    You do NOT need to type the tender ID manually anymore -- it's read
    straight out of the PDF (e.g. "GEM/2026/B/7829782"). If a tender ID
    genuinely can't be found (non-GeM / malformed PDF), a fallback ID is
    generated so the upload still works.

    Expects multipart/form-data:
        file: <PDF file>              (required)
        uploaded_by: user id (int)    (required)
        tender_id: optional manual override
        tender_title: optional manual override
    """
    if "file" not in request.files:
        return jsonify({"error": "No file part in request"}), 400

    file = request.files["file"]
    uploaded_by = request.form.get("uploaded_by")
    manual_tender_id = request.form.get("tender_id", "").strip()
    manual_tender_title = request.form.get("tender_title", "").strip()

    if file.filename == "":
        return jsonify({"error": "A PDF file is required"}), 400

    if not allowed_file(file.filename):
        return jsonify({"error": "Only PDF files are allowed"}), 400

    # Save with a temporary name first (we don't know the tender ID yet)
    temp_name = secure_filename(file.filename)
    temp_path = os.path.join(TENDER_UPLOAD_DIR, temp_name)
    file.save(temp_path)

    # 1. Extract raw text (PyMuPDF, falls back to OCR automatically if needed)
    pdf_result = process_pdf(temp_path)
    extracted_text = pdf_result["text"]

    # 2. Auto-extract tender info from that text
    info = extract_tender_info(extracted_text)

    tender_id = manual_tender_id or info["tender_id"]
    tender_title = manual_tender_title or info["tender_title"]

    # Rename the saved file to match the real tender ID now that we know it
    final_name = secure_filename(tender_id.replace("/", "-")) + ".pdf"
    final_path = os.path.join(TENDER_UPLOAD_DIR, final_name)
    if temp_path != final_path:
        os.replace(temp_path, final_path)
    relative_path = os.path.join("uploads", "tenders", final_name)

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        """INSERT INTO tenders
               (tender_id, tender_title, ministry, department, bid_end_date,
                pdf_path, extracted_text, uploaded_by)
           VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
           ON DUPLICATE KEY UPDATE
               tender_title = VALUES(tender_title),
               ministry = VALUES(ministry),
               department = VALUES(department),
               bid_end_date = VALUES(bid_end_date),
               pdf_path = VALUES(pdf_path),
               extracted_text = VALUES(extracted_text)""",
        (tender_id, tender_title, info["ministry"], info["department"],
         info["bid_end_date"], relative_path, extracted_text, uploaded_by)
    )
    conn.commit()

    cursor.execute("SELECT id FROM tenders WHERE tender_id = %s", (tender_id,))
    tender_db_id = cursor.fetchone()[0]

    # ---- Phase 1: only PERSIST the GST requirement (ignore PAN/MSME/ECS) ----
    # The other categories are still reported back in the response below
    # so the officer can see they exist -- they're just not verified yet
    # (that's future-phase scope).
    requirements_found = info["requirements_detected"]
    gst_detected = any(r["category"] == "GST" for r in requirements_found)

    cursor.execute(
        "SELECT id FROM requirements WHERE tender_id = %s AND category = 'GST'",
        (tender_db_id,)
    )
    existing = cursor.fetchone()

    if gst_detected and not existing:
        cursor.execute(
            """INSERT INTO requirements (tender_id, category, requirement_text, mandatory, source_reference)
               VALUES (%s, 'GST', 'GST Document', TRUE, 'Tender PDF (auto-detected)')""",
            (tender_db_id,)
        )
        conn.commit()

    cursor.close()
    conn.close()

    return jsonify({
        "message": "Tender uploaded and analyzed successfully",
        "tender_db_id": tender_db_id,
        "tender_id": tender_id,
        "tender_id_auto_generated": info["auto_generated_id"],
        "tender_title": tender_title,
        "ministry": info["ministry"],
        "department": info["department"],
        "bid_end_date": info["bid_end_date"],
        "extraction_method": pdf_result["method_used"],
        "page_count": pdf_result["page_count"],
        "requirements_detected": requirements_found,
        "gst_requirement_detected": gst_detected
    }), 201


@app.route("/api/tenders/<int:tender_db_id>", methods=["GET"])
def get_tender(tender_db_id):
    """Returns full tender details + its requirements."""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM tenders WHERE id = %s", (tender_db_id,))
    tender = cursor.fetchone()

    if not tender:
        cursor.close()
        conn.close()
        return jsonify({"error": "Tender not found"}), 404

    cursor.execute("SELECT * FROM requirements WHERE tender_id = %s", (tender_db_id,))
    requirements = cursor.fetchall()

    cursor.close()
    conn.close()

    tender["requirements"] = requirements
    return jsonify(tender), 200


# ------------------------------------------------------------------
# BIDDERS
# ------------------------------------------------------------------

@app.route("/api/bidders", methods=["POST"])
def add_bidder():
    """
    Adds a new bidder under a tender.
    Expects JSON: { "tender_db_id": int, "bidder_name": str, "added_by": int }
    """
    data = request.get_json(force=True)
    tender_db_id = data.get("tender_db_id")
    bidder_name = data.get("bidder_name", "").strip()
    added_by = data.get("added_by")

    if not tender_db_id or not bidder_name:
        return jsonify({"error": "tender_db_id and bidder_name are required"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO bidders (tender_id, bidder_name, added_by) VALUES (%s, %s, %s)",
        (tender_db_id, bidder_name, added_by)
    )
    conn.commit()
    new_id = cursor.lastrowid
    cursor.close()
    conn.close()

    return jsonify({"message": "Bidder added", "bidder_id": new_id}), 201


@app.route("/api/bidders/<int:tender_db_id>", methods=["GET"])
def list_bidders(tender_db_id):
    """Lists all bidders for a given tender."""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM bidders WHERE tender_id = %s", (tender_db_id,))
    bidders = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(bidders), 200


# ------------------------------------------------------------------
# DOCUMENTS
# ------------------------------------------------------------------

@app.route("/api/bidders/<int:bidder_id>/documents", methods=["POST"])
def upload_bidder_document(bidder_id):
    """
    Uploads a bidder's GST certificate PDF, extracts its text and saves it.
    Expects multipart/form-data:
        file: <PDF file>
        document_type: e.g. "GST Certificate" (defaults to that)
    """
    if "file" not in request.files:
        return jsonify({"error": "No file part in request"}), 400

    file = request.files["file"]
    document_type = request.form.get("document_type", "GST Certificate")

    if file.filename == "" or not allowed_file(file.filename):
        return jsonify({"error": "A valid PDF file is required"}), 400

    safe_name = secure_filename(f"bidder{bidder_id}_{file.filename}")
    save_path = os.path.join(BIDDER_DOC_UPLOAD_DIR, safe_name)
    file.save(save_path)

    result = process_pdf(save_path)
    extracted_text = result["text"]

    conn = get_db_connection()
    cursor = conn.cursor()
    relative_path = os.path.join("uploads", "bidder_documents", safe_name)
    cursor.execute(
        """INSERT INTO documents (bidder_id, document_type, file_path, extracted_text)
           VALUES (%s, %s, %s, %s)""",
        (bidder_id, document_type, relative_path, extracted_text)
    )
    conn.commit()
    document_id = cursor.lastrowid
    cursor.close()
    conn.close()

    return jsonify({
        "message": "Document uploaded and text extracted",
        "document_id": document_id,
        "extraction_method": result["method_used"]
    }), 201


# ------------------------------------------------------------------
# GST VERIFICATION
# ------------------------------------------------------------------

@app.route("/api/verify-gst", methods=["POST"])
def verify_gst_route():
    """
    Runs the GST verification engine against a previously uploaded document.
    Expects JSON: { "document_id": int, "bidder_id": int }
    """
    data = request.get_json(force=True)
    document_id = data.get("document_id")
    bidder_id = data.get("bidder_id")

    if not document_id or not bidder_id:
        return jsonify({"error": "document_id and bidder_id are required"}), 400

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM documents WHERE id = %s", (document_id,))
    document = cursor.fetchone()

    cursor.execute("SELECT * FROM bidders WHERE id = %s", (bidder_id,))
    bidder = cursor.fetchone()

    if not document or not bidder:
        cursor.close()
        conn.close()
        return jsonify({"error": "Document or bidder not found"}), 404

    verification = verify_gst(document["extracted_text"], bidder["bidder_name"])

    cursor.execute(
        """INSERT INTO compliance_results
           (bidder_id, document_id, extracted_gstin, matched_company_name, gst_status, result, reason)
           VALUES (%s, %s, %s, %s, %s, %s, %s)""",
        (
            bidder_id,
            document_id,
            verification["extracted_gstin"],
            verification["matched_company_name"],
            verification["gst_status"],
            verification["result"],
            verification["reason"]
        )
    )
    conn.commit()
    result_id = cursor.lastrowid
    cursor.close()
    conn.close()

    verification["result_id"] = result_id
    verification["bidder_name"] = bidder["bidder_name"]
    return jsonify(verification), 200


# ------------------------------------------------------------------
# COMPLIANCE DASHBOARD
# ------------------------------------------------------------------

@app.route("/api/tenders/<int:tender_db_id>/compliance", methods=["GET"])
def tender_compliance(tender_db_id):
    """
    Returns the comparative compliance dashboard data for a tender:
    every bidder + their latest GST verification result.
    """
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM bidders WHERE tender_id = %s", (tender_db_id,))
    bidders = cursor.fetchall()

    dashboard = []
    pass_count = fail_count = review_count = 0

    for bidder in bidders:
        cursor.execute(
            """SELECT * FROM compliance_results
               WHERE bidder_id = %s
               ORDER BY verified_at DESC LIMIT 1""",
            (bidder["id"],)
        )
        latest_result = cursor.fetchone()

        risk = "Medium"
        if latest_result:
            if latest_result["result"] == "PASS":
                risk = "Low"
                pass_count += 1
            elif latest_result["result"] == "FAIL":
                risk = "High"
                fail_count += 1
            else:
                risk = "Medium"
                review_count += 1

        dashboard.append({
            "bidder_id": bidder["id"],
            "bidder_name": bidder["bidder_name"],
            "gstin": latest_result["extracted_gstin"] if latest_result else None,
            "gst_status": latest_result["gst_status"] if latest_result else "Not Verified",
            "result": latest_result["result"] if latest_result else "PENDING",
            "reason": latest_result["reason"] if latest_result else "No document verified yet",
            "risk": risk
        })

    cursor.close()
    conn.close()

    return jsonify({
        "tender_db_id": tender_db_id,
        "total_bidders": len(bidders),
        "pass_count": pass_count,
        "fail_count": fail_count,
        "review_count": review_count,
        "bidders": dashboard
    }), 200


# ------------------------------------------------------------------
# HEALTH CHECK
# ------------------------------------------------------------------

@app.route("/api/health", methods=["GET"])
def health_check():
    return jsonify({"status": "ok", "message": "GST Compliance backend is running"}), 200


if __name__ == "__main__":
    port = int(os.getenv("FLASK_PORT", 5000))
    app.run(debug=True, port=port)
