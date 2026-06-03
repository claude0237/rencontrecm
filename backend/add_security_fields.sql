-- Add security fields to password_resets table
ALTER TABLE password_resets ADD COLUMN wave_count INT DEFAULT 0 AFTER attempts;
ALTER TABLE password_resets ADD COLUMN last_attempt_at DATETIME AFTER wave_count;

-- Add disabled fields to utilisateurs table
ALTER TABLE utilisateurs ADD COLUMN disabled_reason VARCHAR(100) AFTER actif;
ALTER TABLE utilisateurs ADD COLUMN disabled_at DATETIME AFTER disabled_reason;
