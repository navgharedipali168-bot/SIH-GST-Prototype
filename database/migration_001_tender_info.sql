-- ============================================
-- MIGRATION: Add auto-extracted tender info columns
-- Run this ONLY IF you already created the database before
-- (i.e. you already ran the old schema.sql once).
--
-- If you are setting up the database for the FIRST time,
-- you do NOT need this file -- just run schema.sql, it already
-- includes these columns.
-- ============================================

USE gst_compliance_db;

ALTER TABLE tenders ADD COLUMN ministry VARCHAR(150) NULL AFTER tender_title;
ALTER TABLE tenders ADD COLUMN department VARCHAR(150) NULL AFTER ministry;
ALTER TABLE tenders ADD COLUMN bid_end_date VARCHAR(50) NULL AFTER department;
