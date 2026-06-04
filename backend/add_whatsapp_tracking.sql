-- Create table for tracking WhatsApp clicks
CREATE TABLE IF NOT EXISTS whatsapp_clicks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    cliquant_id INT NULL,
    cible_id INT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (cliquant_id) REFERENCES utilisateurs(id) ON DELETE CASCADE,
    FOREIGN KEY (cible_id) REFERENCES utilisateurs(id) ON DELETE CASCADE,
    INDEX idx_cliquant (cliquant_id),
    INDEX idx_cible (cible_id),
    INDEX idx_created_at (created_at)
);

-- Add whatsapp_enabled field to utilisateurs table
ALTER TABLE utilisateurs ADD COLUMN whatsapp_enabled BOOLEAN DEFAULT TRUE AFTER contact_whatsapp;

-- Create table for WhatsApp default message
CREATE TABLE IF NOT EXISTS whatsapp_settings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    default_message VARCHAR(1000) NOT NULL DEFAULT 'Bonjour {nom}, je vous contacte depuis RencontreCm. Votre profil a retenu mon attention.',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Insert default message
INSERT INTO whatsapp_settings (default_message) 
VALUES ('Bonjour {nom}, je vous contacte depuis RencontreCm. Votre profil a retenu mon attention.')
ON DUPLICATE KEY UPDATE default_message = VALUES(default_message);
