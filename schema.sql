-- ============================================================
--  Bibliothèque Intelligente – Schéma MySQL
-- ============================================================

CREATE DATABASE IF NOT EXISTS bibliotheque
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE bibliotheque;

-- ── Utilisateurs ─────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS utilisateurs (
    id_utilisateur  INT           AUTO_INCREMENT PRIMARY KEY,
    nom             VARCHAR(150)  NOT NULL,
    email           VARCHAR(255)  NOT NULL UNIQUE,
    mot_de_passe    VARCHAR(255)  NOT NULL,
    date_creation   DATETIME      DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- ── Livres ────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS livres (
    id_livre             INT          AUTO_INCREMENT PRIMARY KEY,
    titre                VARCHAR(255) NOT NULL,
    auteur               VARCHAR(150) NOT NULL,
    categorie            VARCHAR(100),
    annee_publication    YEAR,
    quantite_disponible  INT          DEFAULT 1,
    statut               ENUM('Disponible','Emprunté','Réservé') DEFAULT 'Disponible',
    maison_publication   VARCHAR(150),
    image_couverture     TEXT,
    description          TEXT,
    date_ajout           DATETIME     DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- ── Données de démonstration ──────────────────────────────────
INSERT INTO livres
    (titre, auteur, categorie, annee_publication,
     quantite_disponible, statut, maison_publication, description)
VALUES
('Les Misérables',
 'Victor Hugo', 'Roman', 1862, 3, 'Disponible', 'Gallimard',
 'Un chef-d''œuvre de la littérature française retraçant la vie de Jean Valjean.'),

('Notre-Dame de Paris',
 'Victor Hugo', 'Roman', 1831, 2, 'Emprunté', 'Gallimard',
 'L''histoire tragique de Quasimodo et Esmeralda dans le Paris médiéval.'),

('Le Petit Prince',
 'Antoine de Saint-Exupéry', 'Conte', 1943, 5, 'Disponible', 'Gallimard',
 'Un conte philosophique et poétique universellement aimé.'),

('Harry Potter à l''École des Sorciers',
 'J.K. Rowling', 'Fantasy', 1997, 3, 'Disponible', 'Bloomsbury',
 'Le début des aventures du jeune sorcier Harry Potter.'),

('1984',
 'George Orwell', 'Science-Fiction', 1949, 1, 'Réservé', 'Secker & Warburg',
 'Un roman dystopique décrivant une société totalitaire sous surveillance absolue.'),

('L''Étranger',
 'Albert Camus', 'Philosophie', 1942, 4, 'Disponible', 'Gallimard',
 'Meursault, un homme indifférent, commet un meurtre absurde sous le soleil algérien.'),

('Dune',
 'Frank Herbert', 'Science-Fiction', 1965, 2, 'Disponible', 'Chilton Books',
 'Un roman épique de science-fiction se déroulant sur la planète désertique Arrakis.'),

('Le Comte de Monte-Cristo',
 'Alexandre Dumas', 'Aventure', 1844, 2, 'Emprunté', 'Pétion',
 'La vengeance méthodique d''Edmond Dantès contre ceux qui l''ont trahi.'),

('Sapiens',
 'Yuval Noah Harari', 'Histoire', 2011, 3, 'Disponible', 'Albin Michel',
 'Une brève histoire de l''humanité depuis les origines jusqu''à nos jours.'),

('L''Art de la Guerre',
 'Sun Tzu', 'Philosophie', 500, 6, 'Disponible', 'Bibliothèque',
 'Traité militaire stratégique devenu une référence universelle en gestion et stratégie.');
