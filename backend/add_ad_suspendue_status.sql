-- Add 'suspendue' status to advertisements table
ALTER TABLE advertisements MODIFY COLUMN statut VARCHAR(20) DEFAULT 'brouillon';
