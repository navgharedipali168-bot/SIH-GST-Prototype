"""
tender_extractor.py
--------------------
Extracts important tender information automatically from the raw text of
ANY GeM tender PDF (not tied to one specific tender).

This runs right after pdf_processor.py pulls the text out of the PDF.

Extracts:
    - tender_id      (e.g. GEM/2026/B/7829782)
    - tender_title   (e.g. HIGH REPETITION RATE PULSED LASER SOURCE)
    - ministry
    - department
    - bid_end_date
    - requirements_detected: list of {category, mandatory, source_reference}
      for whichever of GST / PAN / MSME / NSIC / ECS are mentioned anywhere
      in the tender. Phase 1 only PROCESSES the "GST" one -- the rest are
      reported back so the officer can see they exist, but they are not
      stored/verified yet (future phases).
"""

import re
import time

# GeM tender/bid numbers always follow this pattern regardless of which
# ministry/department/tender it is, so this works for ANY tender.
TENDER_ID_REGEX = r"\bGEM/\d{4}/[A-Z]/\d+\b"

# Keyword categories we look for in the "documents required from seller" /
# general terms sections. Phase 1 only acts on GST; the others are just
# reported as "detected" for future phases.
REQUIREMENT_KEYWORDS = {
    "GST": r"\bGST\b",
    "PAN": r"\bPAN\b",
    "MSME": r"\bMSME\b|\bNSIC\b",
    "ECS": r"\bECS\b",
}


def _first_match_on_line(text: str, label_pattern: str) -> str | None:
    """
    Looks for a line containing `label_pattern` and returns the value.

    GeM tender PDFs are table-based, and when PyMuPDF extracts text the
    label and its value usually land on two SEPARATE lines (label line,
    then value line right after) rather than the same line. This checks
    both cases:
      1. label and value on the same line (label: value)
      2. label on its own line, value on the next non-empty line
    """
    lines = text.splitlines()
    wrapped_pattern = r"(?:" + label_pattern + r")"
    for i, line in enumerate(lines):
        if re.search(wrapped_pattern, line, re.IGNORECASE):
            # Case 1: value might be on the same line, after the label
            same_line_match = re.search(
                wrapped_pattern + r"\s*[:\-]?\s*(\S.*)", line, re.IGNORECASE
            )
            if same_line_match:
                candidate = same_line_match.group(1).strip()
                # Make sure we didn't just re-capture part of the label itself,
                # or a leftover bilingual separator like "/Time" or "/समय"
                if (
                    candidate
                    and not re.fullmatch(wrapped_pattern, candidate, re.IGNORECASE)
                    and not candidate.startswith("/")
                ):
                    return candidate

            # Case 2: look ahead to the next non-empty line
            for next_line in lines[i + 1: i + 3]:
                candidate = next_line.strip()
                if candidate:
                    return candidate
    return None


def extract_tender_id(text: str) -> str | None:
    match = re.search(TENDER_ID_REGEX, text.upper())
    return match.group(0) if match else None


def extract_tender_title(text: str) -> str | None:
    return _first_match_on_line(text, r"Global Tender Title|Tender Title|Bid Title")


def extract_ministry(text: str) -> str | None:
    return _first_match_on_line(text, r"Ministry\s*/\s*State Name|Ministry Name")


def extract_department(text: str) -> str | None:
    return _first_match_on_line(text, r"Department Name")


def extract_bid_end_date(text: str) -> str | None:
    return _first_match_on_line(text, r"Bid End Date\s*/\s*Time|Bid End Date")


def detect_requirements(text: str) -> list:
    """
    Scans the whole tender text for known requirement-category keywords.
    Returns a list of dicts, one per keyword FOUND in the document.
    Phase 1 will only persist/act on the 'GST' entry; the others are
    informational (future phases: PAN, MSME/NSIC, ECS verification).
    """
    detected = []
    for category, pattern in REQUIREMENT_KEYWORDS.items():
        if re.search(pattern, text, re.IGNORECASE):
            detected.append({
                "category": category,
                "mandatory": True,
                "source_reference": "Tender PDF (auto-detected)"
            })
    return detected


def generate_fallback_tender_id() -> str:
    """
    Used only if no GEM/xxxx/x/xxxx pattern is found in the PDF
    (e.g. a non-GeM or malformed tender). Keeps the app usable instead
    of failing the upload.
    """
    return f"TND-{int(time.time())}"


def extract_tender_info(text: str) -> dict:
    """
    Main entry point used by app.py. Runs all the individual extractors
    and returns one combined dict describing the tender.
    """
    tender_id = extract_tender_id(text)
    auto_generated_id = False

    if not tender_id:
        tender_id = generate_fallback_tender_id()
        auto_generated_id = True

    return {
        "tender_id": tender_id,
        "auto_generated_id": auto_generated_id,
        "tender_title": extract_tender_title(text) or "Untitled Tender",
        "ministry": extract_ministry(text),
        "department": extract_department(text),
        "bid_end_date": extract_bid_end_date(text),
        "requirements_detected": detect_requirements(text),
    }


if __name__ == "__main__":
    import sys
    from pdf_processor import process_pdf

    if len(sys.argv) > 1:
        result = process_pdf(sys.argv[1])
        info = extract_tender_info(result["text"])
        import json
        print(json.dumps(info, indent=2))
    else:
        print("Usage: python tender_extractor.py <path_to_pdf>")
