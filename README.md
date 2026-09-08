# SIH GST Compliance Prototype — Phase 1 (MVP)

Prototype for Smart India Hackathon Problem Statement 26100:
**"AI-Powered Integrated Bid Compliance Verification Platform for GeM Procurement"**

This is **Phase 1 only** — it handles **GST compliance verification**, nothing else
(PAN, MSME/NSIC, ECS are intentionally out of scope for now).

---

## 1. What this does

**Works with ANY GeM tender PDF you upload** — you don't type the tender
ID manually. The backend (`tender_extractor.py`) reads the tender straight
out of the PDF and pulls out:
- Tender/Bid ID (e.g. `GEM/2026/B/7829782`)
- Tender title
- Ministry / Department
- Bid end date
- Which requirement categories are mentioned (GST, PAN, MSME/NSIC, ECS)

Phase 1 only **acts** on the GST requirement (verifies it against the mock
GST database and produces PASS/FAIL/REVIEW per bidder) — the other
categories are shown as "detected" for visibility, ready for future phases.


```
Verified User Login
      ↓
Upload Tender PDF
      ↓
Extract Tender Text (PyMuPDF, OCR fallback)
      ↓
Identify GST Requirement
      ↓
Add/Select Bidder
      ↓
Upload Bidder GST Certificate
      ↓
Extract GSTIN
      ↓
Compare with Mock GST Database (MySQL)
      ↓
Verification Engine → PASS / FAIL / REVIEW
      ↓
Comparative Bidder Dashboard
```

Uses a **mock GST database** — no real government API calls.

## 2. Reference Tender (proof / test case)

The real GeM tender used to build and test this prototype is kept at:

```
docs/source_tenders/GEM-2026-B-7829782.pdf
```

Details:

| Field | Value |
|---|---|
| Tender/Bid Number | GEM/2026/B/7829782 |
| Ministry | Ministry of Defence |
| Department | Defence R&D |
| Buyer requirement | GST, PAN, MSME/NSIC, ECS Details (Phase 1 processes **GST only**) |

The same file is pre-copied into `backend/uploads/tenders/` so you can immediately
test the upload flow with a real document.

## 3. Tech Stack

- Frontend: React.js + Tailwind CSS
- Backend: Python + Flask
- PDF Processing: PyMuPDF (+ Tesseract OCR fallback for scanned PDFs)
- Database: MySQL
- Testing: Postman (`backend/postman_collection.json`)

## 4. Project Structure

```
SIH-GST-Prototype/
├── backend/
│   ├── app.py                  # Flask routes
│   ├── database.py             # MySQL connection
│   ├── pdf_processor.py        # PyMuPDF + OCR
│   ├── gst_verification.py     # GSTIN extraction + PASS/FAIL/REVIEW logic
│   ├── requirements.txt
│   ├── .env.example
│   ├── postman_collection.json
│   └── uploads/
│       ├── tenders/
│       └── bidder_documents/
├── frontend/
│   ├── src/
│   │   ├── pages/               (Login, Dashboard, TenderUpload, BidderManagement,
│   │   │                          GSTVerification, ComparativeDashboard)
│   │   ├── components/Navbar.jsx
│   │   ├── api.js
│   │   ├── App.js
│   │   └── index.js
│   ├── package.json
│   └── tailwind.config.js
├── database/
│   ├── schema.sql
│   └── dummy_data.sql
└── docs/
    └── source_tenders/GEM-2026-B-7829782.pdf   (proof/reference tender)
```

## 5. Setup — Step by Step

### 5.1 Database

**First-time setup:**

```bash
mysql -u root -p
```

Inside the MySQL prompt:

```sql
source database/schema.sql;
source database/dummy_data.sql;
```

Verify:

```sql
USE gst_compliance_db;
SHOW TABLES;
SELECT * FROM users;
SELECT * FROM gst_records;
```

You should see 7 tables and mock users/GST records.

**Already had the database set up before this update?** Run the migration
instead of recreating everything (keeps your existing data):

```sql
source database/migration_001_tender_info.sql;
```

This adds 3 new columns (`ministry`, `department`, `bid_end_date`) to the
`tenders` table that the auto-extraction feature needs.

### 5.2 Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

pip install -r requirements.txt
```

Install Tesseract OCR separately (only needed for scanned PDFs):
- Ubuntu/Debian: `sudo apt install tesseract-ocr`
- Mac: `brew install tesseract`
- Windows: download installer from https://github.com/UB-Mannheim/tesseract/wiki

Copy the env file and fill in your MySQL password:

```bash
cp .env.example .env
```

Edit `.env`:
```
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=<your_mysql_password>
DB_NAME=gst_compliance_db
```

Test the DB connection:

```bash
python database.py
```

Expected output: `✅ Successfully connected to MySQL database: gst_compliance_db`

Run the backend:

```bash
python app.py
```

Expected: Flask running on `http://127.0.0.1:5000`

Test with a browser or curl:
```
GET http://localhost:5000/api/health
→ {"status": "ok", "message": "GST Compliance backend is running"}
```

### 5.3 Test with Postman

Import `backend/postman_collection.json` into Postman and run requests in this order:
1. Health Check
2. Login (Verified Officer)
3. Upload Tender PDF — attach `docs/source_tenders/GEM-2026-B-7829782.pdf` as the `file` field
4. Add Bidder
5. Upload Bidder GST Document — attach any sample GST certificate PDF containing a GSTIN like `27ABCDE1234F1Z5`
6. Verify GST
7. Get Tender Compliance Dashboard

### 5.4 Frontend

```bash
cd frontend
npm install
npm start
```

Opens at `http://localhost:3000`. Login with:
- `officer@gem.gov.in` / `officer123` (verified — can upload)
- `guest@example.com` / `guest123` (NOT verified — upload blocked, as required)

## 6. Mock GST Data (for testing)

| GSTIN | Company | Status | Expected Result |
|---|---|---|---|
| 27ABCDE1234F1Z5 | ABC Technologies | Active | PASS |
| 27XYZAB5678C1Z9 | XYZ Systems | Cancelled | FAIL |
| 27PQRAB9012D1Z3 | PQR Industries | Active | PASS |
| (any unknown GSTIN) | — | — | REVIEW |

To test PASS/FAIL/REVIEW quickly without scanning real certificates, create a simple
text-based PDF containing lines like:

```
GSTIN: 27ABCDE1234F1Z5
Company Name: ABC Technologies
```

## 7. What's intentionally NOT built in Phase 1

PAN, MSME/NSIC, ECS, Udyam, OEM, EPFO/ESIC, Startup India, DigiLocker, blacklisting,
real government API integration, RAG/vector DB/LLM/ML models, microservices, complex auth,
payments. These are future phases — only the database schema leaves room for them
(e.g. `requirements.category` and `documents.document_type` are free-text fields so
new categories can be added later without restructuring the schema).

## 8. Success Criteria (Phase 1)

- [x] Login as verified procurement officer
- [x] Upload GeM tender PDF
- [x] Extract tender text
- [x] Detect/store GST requirement
- [x] Add 2-3 dummy bidders
- [x] Upload GST certificates
- [x] Extract GSTIN
- [x] Verify against mock MySQL GST data
- [x] Generate PASS / FAIL / REVIEW
- [x] Comparative dashboard across bidders
