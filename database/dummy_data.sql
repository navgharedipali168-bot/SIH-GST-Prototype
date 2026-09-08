-- ============================================
-- MOCK DATA -- for prototype/testing only
-- This data is FAKE and used only to simulate
-- a real GST government database.
-- ============================================

USE gst_compliance_db;

-- ---------------------------------
-- Mock Users
-- NOTE: Passwords are plain text ONLY for this prototype (not production-safe)
-- ---------------------------------
INSERT INTO users (name, email, password, role, is_verified) VALUES
('Admin User', 'admin@gem.gov.in', 'admin123', 'Admin', TRUE),
('Sunil Reddy', 'officer@gem.gov.in', 'officer123', 'Procurement Officer', TRUE),
('Random Guest', 'guest@example.com', 'guest123', 'Guest', FALSE);

-- ---------------------------------
-- Mock GST Database (clearly labeled MOCK DATA)
-- ---------------------------------
INSERT INTO gst_records (gstin, company_name, status) VALUES
('27ABCDE1234F1Z5', 'ABC Technologies', 'Active'),
('27XYZAB5678C1Z9', 'XYZ Systems', 'Cancelled'),
('27PQRAB9012D1Z3', 'PQR Industries', 'Active');

-- ---------------------------------
-- Sample Tender (from the real GeM tender PDF used as test case)
-- Source: docs/source_tenders/GEM-2026-B-7829782.pdf
-- ---------------------------------
INSERT INTO tenders (tender_id, tender_title, pdf_path, uploaded_by) VALUES
('GEM/2026/B/7829782', 'HIGH REPETITION RATE PULSED LASER SOURCE',
 'uploads/tenders/GEM-2026-B-7829782.pdf', 2);

-- ---------------------------------
-- Sample Requirement extracted from that tender (GST only, Phase 1 scope)
-- ---------------------------------
INSERT INTO requirements (tender_id, category, requirement_text, mandatory, source_reference) VALUES
(1, 'GST', 'GST Document', TRUE, 'Tender PDF / Page 4');
