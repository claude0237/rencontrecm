-- Create table for ad packs (pricing packages)
CREATE TABLE IF NOT EXISTS ad_packs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nom VARCHAR(100) NOT NULL,
    description TEXT,
    prix DECIMAL(10, 2) NOT NULL,
    duree_jours INT NOT NULL,
    actif BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Insert default ad packs
INSERT INTO ad_packs (nom, description, prix, duree_jours) VALUES 
('Pack Bronze', 'Publicité pendant 7 jours', 5000, 7),
('Pack Argent', 'Publicité pendant 15 jours', 10000, 15),
('Pack Or', 'Publicité pendant 30 jours', 20000, 30)
ON DUPLICATE KEY UPDATE nom = VALUES(nom);

-- Create table for advertisements
CREATE TABLE IF NOT EXISTS advertisements (
    id INT AUTO_INCREMENT PRIMARY KEY,
    utilisateur_id INT NOT NULL,
    titre VARCHAR(200) NOT NULL,
    description TEXT NOT NULL,
    image_url VARCHAR(500),
    numero_contact VARCHAR(50),
    whatsapp VARCHAR(50),
    duree_jours INT NOT NULL,
    statut ENUM('brouillon', 'en_attente', 'validee', 'rejetee', 'expiree') DEFAULT 'brouillon',
    pack_id INT,
    date_creation DATETIME DEFAULT CURRENT_TIMESTAMP,
    date_debut_validite DATETIME,
    date_fin_validite DATETIME,
    paiement_effectue BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (utilisateur_id) REFERENCES utilisateurs(id) ON DELETE CASCADE,
    FOREIGN KEY (pack_id) REFERENCES ad_packs(id) ON DELETE SET NULL,
    INDEX idx_utilisateur (utilisateur_id),
    INDEX idx_statut (statut),
    INDEX idx_date_fin (date_fin_validite)
);
