-- ============================================
-- SIH GST Compliance Prototype - Database Schema
-- Phase 1: GST Compliance Only
-- ============================================

CREATE DATABASE IF NOT EXISTS gst_compliance_db;
USE gst_compliance_db;

-- ---------------------------------
-- 1. USERS TABLE
-- ---------------------------------
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL,          -- e.g. 'Admin', 'Procurement Officer'
    is_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ---------------------------------
-- 2. TENDERS TABLE
-- ---------------------------------
CREATE TABLE IF NOT EXISTS tenders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    tender_id VARCHAR(100) UNIQUE NOT NULL,   -- e.g. GEM/2026/B/7829782 (auto-extracted)
    tender_title VARCHAR(255),                -- auto-extracted from PDF
    ministry VARCHAR(150),                    -- auto-extracted from PDF
    department VARCHAR(150),                  -- auto-extracted from PDF
    bid_end_date VARCHAR(50),                 -- auto-extracted from PDF
    pdf_path VARCHAR(255),                     -- path to uploaded PDF
    extracted_text LONGTEXT,                  -- full extracted text from PDF
    uploaded_by INT,                          -- FK to users.id
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (uploaded_by) REFERENCES users(id)
);

-- ---------------------------------
-- 3. REQUIREMENTS TABLE
-- ---------------------------------
CREATE TABLE IF NOT EXISTS requirements (
    id INT AUTO_INCREMENT PRIMARY KEY,
    tender_id INT NOT NULL,                   -- FK to tenders.id
    category VARCHAR(50) NOT NULL,            -- 'GST' for Phase 1
    requirement_text VARCHAR(255),            -- e.g. 'GST Document'
    mandatory BOOLEAN DEFAULT TRUE,
    source_reference VARCHAR(100),            -- e.g. 'Tender PDF / Page 4'
    FOREIGN KEY (tender_id) REFERENCES tenders(id)
);

-- ---------------------------------
-- 4. BIDDERS TABLE
-- ---------------------------------
CREATE TABLE IF NOT EXISTS bidders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    tender_id INT NOT NULL,                   -- FK to tenders.id
    bidder_name VARCHAR(150) NOT NULL,
    added_by INT,                             -- FK to users.id
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (tender_id) REFERENCES tenders(id),
    FOREIGN KEY (added_by) REFERENCES users(id)
);

-- ---------------------------------
-- 5. DOCUMENTS TABLE
-- ---------------------------------
CREATE TABLE IF NOT EXISTS documents (
    id INT AUTO_INCREMENT PRIMARY KEY,
    bidder_id INT NOT NULL,                   -- FK to bidders.id
    document_type VARCHAR(50) NOT NULL,       -- 'GST Certificate' for Phase 1
    file_path VARCHAR(255) NOT NULL,
    extracted_text LONGTEXT,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (bidder_id) REFERENCES bidders(id)
);

-- ---------------------------------
-- 6. GST_RECORDS TABLE (MOCK DATA)
-- ---------------------------------
CREATE TABLE IF NOT EXISTS gst_records (
    id INT AUTO_INCREMENT PRIMARY KEY,
    gstin VARCHAR(20) UNIQUE NOT NULL,
    company_name VARCHAR(150) NOT NULL,
    status VARCHAR(20) NOT NULL               -- 'Active' or 'Cancelled'
);

-- ---------------------------------
-- 7. COMPLIANCE_RESULTS TABLE
-- ---------------------------------
CREATE TABLE IF NOT EXISTS compliance_results (
    id INT AUTO_INCREMENT PRIMARY KEY,
    bidder_id INT NOT NULL,                   -- FK to bidders.id
    document_id INT,                          -- FK to documents.id
    extracted_gstin VARCHAR(20),
    matched_company_name VARCHAR(150),
    gst_status VARCHAR(20),
    result VARCHAR(20) NOT NULL,              -- PASS / FAIL / REVIEW
    reason VARCHAR(255),                      -- why this result was given
    verified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (bidder_id) REFERENCES bidders(id),
    FOREIGN KEY (document_id) REFERENCES documents(id)
);
