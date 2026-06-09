-- Augmenter la longueur de la colonne type dans la table admin_notifications
ALTER TABLE admin_notifications MODIFY COLUMN type VARCHAR(50);
