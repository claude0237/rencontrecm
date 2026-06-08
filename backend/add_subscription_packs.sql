-- Table pour les packs d'abonnement
CREATE TABLE IF NOT EXISTS subscription_pack (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nom VARCHAR(50) NOT NULL UNIQUE,
    niveau ENUM('gratuit', 'bronze', 'silver', 'gold', 'vip') NOT NULL,
    prix DECIMAL(10, 2) NOT NULL DEFAULT 0,
    duree_jours INT NOT NULL,
    profils_consultables_par_jour INT DEFAULT 5,
    contacts_whatsapp_par_jour INT DEFAULT 0,
    appels_directs_par_jour INT DEFAULT 0,
    mise_en_avant_pourcentage INT DEFAULT 0,
    badge VARCHAR(20) DEFAULT NULL,
    actif BOOLEAN DEFAULT TRUE,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Table pour les abonnements utilisateurs (sans foreign keys d'abord)
CREATE TABLE IF NOT EXISTS user_subscription (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    pack_id INT NOT NULL,
    date_debut TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    date_fin TIMESTAMP NOT NULL,
    statut ENUM('actif', 'expire', 'annule') DEFAULT 'actif',
    profils_consultes_aujourdhui INT DEFAULT 0,
    contacts_whatsapp_aujourdhui INT DEFAULT 0,
    appels_directs_aujourdhui INT DEFAULT 0,
    dernier_reset_quotas TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    methode_paiement VARCHAR(50) DEFAULT 'manuel',
    reference_paiement VARCHAR(100) DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Ajouter les foreign keys après création des tables
ALTER TABLE user_subscription
ADD CONSTRAINT fk_user_subscription_user
FOREIGN KEY (user_id) REFERENCES utilisateurs(id) ON DELETE CASCADE;

ALTER TABLE user_subscription
ADD CONSTRAINT fk_user_subscription_pack
FOREIGN KEY (pack_id) REFERENCES subscription_pack(id) ON DELETE CASCADE;

-- Index pour optimiser les requêtes
CREATE INDEX idx_user_subscription_user_id ON user_subscription(user_id);
CREATE INDEX idx_user_subscription_statut ON user_subscription(statut);
CREATE INDEX idx_user_subscription_date_fin ON user_subscription(date_fin);
CREATE INDEX idx_subscription_pack_niveau ON subscription_pack(niveau);
CREATE INDEX idx_subscription_pack_actif ON subscription_pack(actif);

-- Insérer les packs par défaut
INSERT INTO subscription_pack (nom, niveau, prix, duree_jours, profils_consultables_par_jour, contacts_whatsapp_par_jour, appels_directs_par_jour, mise_en_avant_pourcentage, badge, description) VALUES
('Découverte', 'gratuit', 0, 7, 5, 0, 0, 0, NULL, 'Pack gratuit d''essai pour découvrir la plateforme'),
('Bronze', 'bronze', 5000, 30, -1, 5, 3, 0, 'Bronze', 'Accès complet avec limitations quotidiennes'),
('Silver', 'silver', 12000, 90, -1, 15, 10, 20, 'Silver', 'Avantages améliorés avec mise en avant légère'),
('Gold', 'gold', 25000, 180, -1, -1, -1, 50, 'Gold', 'Accès premium avec mise en avant importante'),
('VIP', 'vip', 45000, 365, -1, -1, -1, 100, 'VIP', 'Expérience ultime avec positionnement premium');
