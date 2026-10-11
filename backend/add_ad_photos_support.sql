-- Migration SQL pour ajouter le support de photos multiples aux annonces

-- Ajouter le champ nombre_photos_max à la table ad_packs (s'il n'existe pas déjà)
SET @column_exists = (
    SELECT COUNT(*)
    FROM information_schema.columns
    WHERE table_name = 'ad_packs'
    AND column_name = 'nombre_photos_max'
    AND table_schema = DATABASE()
);

SET @sql = IF(@column_exists = 0,
    'ALTER TABLE ad_packs ADD COLUMN nombre_photos_max INT DEFAULT 1 AFTER duree_jours',
    'SELECT "Column nombre_photos_max already exists" AS message'
);
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- Ajouter le champ photos à la table advertisements (s'il n'existe pas déjà)
SET @column_exists = (
    SELECT COUNT(*)
    FROM information_schema.columns
    WHERE table_name = 'advertisements'
    AND column_name = 'photos'
    AND table_schema = DATABASE()
);

SET @sql = IF(@column_exists = 0,
    'ALTER TABLE advertisements ADD COLUMN photos TEXT AFTER image_url',
    'SELECT "Column photos already exists" AS message'
);
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- Ajouter le champ photo_principale à la table advertisements (s'il n'existe pas déjà)
SET @column_exists = (
    SELECT COUNT(*)
    FROM information_schema.columns
    WHERE table_name = 'advertisements'
    AND column_name = 'photo_principale'
    AND table_schema = DATABASE()
);

SET @sql = IF(@column_exists = 0,
    'ALTER TABLE advertisements ADD COLUMN photo_principale INT DEFAULT 0 AFTER photos',
    'SELECT "Column photo_principale already exists" AS message'
);
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- Mettre à jour les packs existants avec une valeur par défaut
UPDATE ad_packs SET nombre_photos_max = 1 WHERE nombre_photos_max IS NULL;
