-- Remove telephone column and make contact_direct NOT NULL and UNIQUE
ALTER TABLE utilisateurs DROP COLUMN telephone;
ALTER TABLE utilisateurs MODIFY COLUMN contact_direct VARCHAR(50) NOT NULL;
ALTER TABLE utilisateurs ADD UNIQUE INDEX idx_contact_direct (contact_direct);
