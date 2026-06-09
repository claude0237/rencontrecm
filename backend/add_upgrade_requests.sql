-- Table pour les demandes d'upgrade d'abonnement
CREATE TABLE IF NOT EXISTS subscription_upgrade_request (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    pack_id INT NOT NULL,
    methode_paiement ENUM('manuel', 'mobile', 'carte') DEFAULT 'manuel',
    statut ENUM('en_attente', 'approuve', 'refuse') DEFAULT 'en_attente',
    reference_paiement VARCHAR(100) DEFAULT NULL,
    message TEXT,
    admin_notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    processed_at TIMESTAMP NULL,
    processed_by INT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Ajouter les foreign keys
ALTER TABLE subscription_upgrade_request
ADD CONSTRAINT fk_upgrade_request_user
FOREIGN KEY (user_id) REFERENCES utilisateurs(id) ON DELETE CASCADE;

ALTER TABLE subscription_upgrade_request
ADD CONSTRAINT fk_upgrade_request_pack
FOREIGN KEY (pack_id) REFERENCES subscription_pack(id) ON DELETE CASCADE;

ALTER TABLE subscription_upgrade_request
ADD CONSTRAINT fk_upgrade_request_admin
FOREIGN KEY (processed_by) REFERENCES utilisateurs(id) ON DELETE SET NULL;

-- Index pour optimiser les requêtes
CREATE INDEX idx_upgrade_request_user_id ON subscription_upgrade_request(user_id);
CREATE INDEX idx_upgrade_request_statut ON subscription_upgrade_request(statut);
CREATE INDEX idx_upgrade_request_created_at ON subscription_upgrade_request(created_at);
