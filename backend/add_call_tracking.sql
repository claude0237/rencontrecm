-- Create table for tracking call initiations
CREATE TABLE IF NOT EXISTS appels (
    id INT AUTO_INCREMENT PRIMARY KEY,
    appelant_id INT NOT NULL,
    appele_id INT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (appelant_id) REFERENCES utilisateurs(id) ON DELETE CASCADE,
    FOREIGN KEY (appele_id) REFERENCES utilisateurs(id) ON DELETE CASCADE,
    INDEX idx_appelant (appelant_id),
    INDEX idx_appele (appele_id),
    INDEX idx_created_at (created_at)
);
