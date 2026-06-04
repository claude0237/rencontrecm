-- Create table for admin notifications
CREATE TABLE IF NOT EXISTS admin_notifications (
    id INT AUTO_INCREMENT PRIMARY KEY,
    type ENUM('nouvelle_publicite', 'paiement_publicitaire', 'autre') NOT NULL,
    titre VARCHAR(200) NOT NULL,
    message TEXT NOT NULL,
    advertisement_id INT,
    utilisateur_id INT,
    lue BOOLEAN DEFAULT FALSE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (advertisement_id) REFERENCES advertisements(id) ON DELETE CASCADE,
    FOREIGN KEY (utilisateur_id) REFERENCES utilisateurs(id) ON DELETE CASCADE,
    INDEX idx_lue (lue),
    INDEX idx_type (type),
    INDEX idx_created_at (created_at)
);
