-- Create table for advertisement validation history
CREATE TABLE IF NOT EXISTS ad_validation_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    advertisement_id INT NOT NULL,
    admin_id INT NOT NULL,
    action ENUM('validee', 'rejetee', 'suspendue') NOT NULL,
    motif_rejet TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (advertisement_id) REFERENCES advertisements(id) ON DELETE CASCADE,
    FOREIGN KEY (admin_id) REFERENCES utilisateurs(id) ON DELETE CASCADE,
    INDEX idx_advertisement (advertisement_id),
    INDEX idx_admin (admin_id),
    INDEX idx_action (action)
);
