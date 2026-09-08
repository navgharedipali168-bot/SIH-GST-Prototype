"""
gst_verification.py
--------------------
Phase 1 verification engine. Handles ONLY the GST compliance category.

Responsibilities:
1. Extract a GSTIN pattern from raw text (extracted from a bidder's
   GST certificate PDF).
2. Look up that GSTIN in the mock `gst_records` table.
3. Decide PASS / FAIL / REVIEW based on simple, explainable rules.

Rules (as specified in the project brief):
    PASS   -> GSTIN found in mock DB, company name matches, status = Active
    FAIL   -> GSTIN found in mock DB, but status = Cancelled/Inactive
    REVIEW -> GSTIN not found / company name mismatch / GSTIN not
              extractable / any uncertain case
"""

import re
from database import get_db_connection

# Standard GSTIN pattern: 15 characters
# 2 digits (state code) + 10 chars (PAN) + 1 digit (entity code)
# + 1 letter (default 'Z') + 1 alphanumeric (checksum)
GSTIN_REGEX = r"\b\d{2}[A-Z]{5}\d{4}[A-Z]{1}\d[A-Z]\d[A-Z]\b|\b\d{2}[A-Z]{5}\d{4}[A-Z]\d[A-Z][A-Z\d]\b"

# A looser, more forgiving pattern that matches real-world GSTIN formats
GSTIN_REGEX_LOOSE = r"\b\d{2}[A-Z]{5}\d{4}[A-Z]\d[A-Z\d][A-Z\d]\b"


def extract_gstin(text: str) -> str | None:
    """
    Scans extracted document text and returns the first GSTIN-looking
    string it finds, or None if nothing matches.
    """
    if not text:
        return None

    cleaned = text.upper()
    match = re.search(GSTIN_REGEX_LOOSE, cleaned)
    if match:
        return match.group(0)
    return None


def normalize_name(name: str) -> str:
    """Lowercases and strips extra spaces/punctuation for loose name comparison."""
    if not name:
        return ""
    return re.sub(r"[^a-z0-9]", "", name.lower())


def lookup_gst_record(gstin: str) -> dict | None:
    """
    Looks up a GSTIN in the mock gst_records table.
    Returns a dict with company_name and status, or None if not found.
    """
    conn = get_db_connection()
    if conn is None:
        return None

    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT gstin, company_name, status FROM gst_records WHERE gstin = %s",
        (gstin,)
    )
    record = cursor.fetchone()
    cursor.close()
    conn.close()
    return record


def verify_gst(extracted_text: str, bidder_name_on_file: str) -> dict:
    """
    Main verification function used by app.py.

    Args:
        extracted_text: raw text pulled from the bidder's uploaded GST document
        bidder_name_on_file: the bidder name as entered in our `bidders` table
                              (used only for a loose sanity check against the
                              company name found in the mock GST record)

    Returns a dict:
        {
            "extracted_gstin": str or None,
            "matched_company_name": str or None,
            "gst_status": str or None,
            "result": "PASS" | "FAIL" | "REVIEW",
            "reason": str   (human-readable explanation for the officer)
        }
    """
    gstin = extract_gstin(extracted_text)

    if not gstin:
        return {
            "extracted_gstin": None,
            "matched_company_name": None,
            "gst_status": None,
            "result": "REVIEW",
            "reason": "GSTIN could not be extracted from the uploaded document. "
                      "Document may be unclear or in an unexpected format."
        }

    record = lookup_gst_record(gstin)

    if record is None:
        return {
            "extracted_gstin": gstin,
            "matched_company_name": None,
            "gst_status": None,
            "result": "REVIEW",
            "reason": f"GSTIN {gstin} was extracted but not found in the GST database "
                      f"(mock). Needs manual verification by a procurement officer."
        }

    # Loose company-name comparison (bidder-entered name vs mock DB record)
    name_matches = normalize_name(bidder_name_on_file) in normalize_name(record["company_name"]) \
        or normalize_name(record["company_name"]) in normalize_name(bidder_name_on_file)

    if not name_matches:
        return {
            "extracted_gstin": gstin,
            "matched_company_name": record["company_name"],
            "gst_status": record["status"],
            "result": "REVIEW",
            "reason": f"GSTIN {gstin} found, but the registered company name "
                      f"'{record['company_name']}' does not clearly match the "
                      f"bidder name '{bidder_name_on_file}'. Needs manual check."
        }

    if record["status"].lower() == "active":
        return {
            "extracted_gstin": gstin,
            "matched_company_name": record["company_name"],
            "gst_status": record["status"],
            "result": "PASS",
            "reason": f"GSTIN {gstin} verified. Company '{record['company_name']}' "
                      f"is Active in the GST database (mock)."
        }
    else:
        return {
            "extracted_gstin": gstin,
            "matched_company_name": record["company_name"],
            "gst_status": record["status"],
            "result": "FAIL",
            "reason": f"GSTIN {gstin} found, but status is "
                      f"'{record['status']}' (not Active)."
        }


if __name__ == "__main__":
    # Quick manual test
    sample_text = "GSTIN: 27ABCDE1234F1Z5   Company Name: ABC Technologies Pvt Ltd"
    print(verify_gst(sample_text, "ABC Technologies"))
