-- ============================================================
--  SUNU KIRAY — Plateforme numérique de santé au Sénégal
--  "Notre Santé" en Wolof
--  Projet PPP 2025-2026 | DIC 1 / DGI / ESP / UCAD
--  Encadrant : Dr Mangoné FALL
-- ============================================================
--  Tables :
--    1. utilisateurs          — comptes de tous les acteurs
--    2. structures_sante      — hôpitaux et centres de santé
--    3. medecins              — profil médecin (lié à utilisateurs)
--    4. services              — spécialités par structure
--    5. disponibilites        — créneaux horaires des médecins
--    6. rendez_vous           — réservations patients
--    7. alertes               — surcharges détectées
--    8. redeplois             — missions temporaires
--    9. notifications         — messages envoyés aux utilisateurs
--   10. rapports              — statistiques générées
-- ============================================================

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ============================================================
-- BASE DE DONNÉES
-- ============================================================
CREATE DATABASE IF NOT EXISTS sunu_kiray
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE sunu_kiray;


-- ============================================================
-- TABLE 1 : UTILISATEURS
-- Tous les acteurs : patients, médecins, administrateurs
-- ============================================================
CREATE TABLE IF NOT EXISTS utilisateurs (
  id              INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  nom             VARCHAR(80)  NOT NULL,
  prenom          VARCHAR(80)  NOT NULL,
  email           VARCHAR(150) NOT NULL UNIQUE,
  telephone       VARCHAR(20)  NOT NULL,
  mot_de_passe    VARCHAR(255) NOT NULL COMMENT 'Stocké en hash bcrypt',
  role            ENUM('patient', 'medecin', 'administrateur') NOT NULL DEFAULT 'patient',
  date_naissance  DATE         NULL,
  sexe            ENUM('masculin', 'feminin', 'autre') NULL,
  adresse         VARCHAR(255) NULL,
  ville           VARCHAR(100) NULL,
  photo_profil    VARCHAR(255) NULL COMMENT 'Chemin relatif vers le fichier image',
  est_actif       BOOLEAN      NOT NULL DEFAULT TRUE,
  token_reset     VARCHAR(255) NULL COMMENT 'Token de réinitialisation du mot de passe',
  token_expire_le DATETIME     NULL,
  derniere_connexion DATETIME  NULL,
  created_at      TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at      TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

  INDEX idx_email   (email),
  INDEX idx_role    (role),
  INDEX idx_actif   (est_actif)
) ENGINE=InnoDB COMMENT='Comptes de tous les acteurs de la plateforme';


-- ============================================================
-- TABLE 2 : STRUCTURES_SANTE
-- Hôpitaux, centres de santé, postes de santé
-- ============================================================
CREATE TABLE IF NOT EXISTS structures_sante (
  id                INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  nom               VARCHAR(150) NOT NULL,
  type_structure    ENUM('hopital', 'centre_sante', 'poste_sante', 'clinique_privee') NOT NULL,
  adresse           VARCHAR(255) NOT NULL,
  ville             VARCHAR(100) NOT NULL,
  region            VARCHAR(100) NOT NULL,
  telephone         VARCHAR(20)  NULL,
  email             VARCHAR(150) NULL,
  latitude          DECIMAL(10, 7) NULL COMMENT 'Coordonnée GPS pour la carte',
  longitude         DECIMAL(10, 7) NULL COMMENT 'Coordonnée GPS pour la carte',
  capacite_journaliere INT UNSIGNED NOT NULL DEFAULT 50 COMMENT 'Nombre max de patients par jour',
  charge_actuelle   INT UNSIGNED NOT NULL DEFAULT 0  COMMENT 'Patients en attente ou pris en charge aujourd\'hui',
  seuil_alerte      INT UNSIGNED NOT NULL DEFAULT 40  COMMENT 'Déclenchement alerte si charge_actuelle >= seuil',
  statut            ENUM('actif', 'inactif', 'maintenance') NOT NULL DEFAULT 'actif',
  heure_ouverture   TIME         NOT NULL DEFAULT '07:00:00',
  heure_fermeture   TIME         NOT NULL DEFAULT '18:00:00',
  description       TEXT         NULL,
  created_at        TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at        TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

  INDEX idx_region  (region),
  INDEX idx_statut  (statut),
  INDEX idx_charge  (charge_actuelle)
) ENGINE=InnoDB COMMENT='Hôpitaux et centres de santé au Sénégal';


-- ============================================================
-- TABLE 3 : MEDECINS
-- Profil étendu d'un utilisateur de rôle "medecin"
-- ============================================================
CREATE TABLE IF NOT EXISTS medecins (
  id                   INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  utilisateur_id       INT UNSIGNED NOT NULL UNIQUE,
  structure_id         INT UNSIGNED NOT NULL COMMENT 'Structure d\'affectation principale',
  specialite           VARCHAR(100) NOT NULL,
  numero_ordre         VARCHAR(50)  NOT NULL UNIQUE COMMENT 'Numéro au Conseil National de l\'Ordre des Médecins',
  grade                ENUM('generaliste', 'specialiste', 'chirurgien', 'interne', 'resident') NOT NULL DEFAULT 'generaliste',
  disponibilite        ENUM('disponible', 'en_consultation', 'en_mission', 'absent', 'conge') NOT NULL DEFAULT 'disponible',
  peut_etre_redeploye  BOOLEAN NOT NULL DEFAULT TRUE COMMENT 'Accepte les missions temporaires',
  rayon_deploiement_km INT UNSIGNED NOT NULL DEFAULT 30 COMMENT 'Distance max pour redéploiement',
  nb_consultations_jour INT UNSIGNED NOT NULL DEFAULT 0,
  bio                  TEXT NULL,
  created_at           TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at           TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

  FOREIGN KEY (utilisateur_id) REFERENCES utilisateurs(id) ON DELETE CASCADE,
  FOREIGN KEY (structure_id)   REFERENCES structures_sante(id) ON DELETE RESTRICT,

  INDEX idx_structure   (structure_id),
  INDEX idx_specialite  (specialite),
  INDEX idx_disponibilite (disponibilite)
) ENGINE=InnoDB COMMENT='Profil médical des médecins inscrits';


-- ============================================================
-- TABLE 4 : SERVICES
-- Spécialités disponibles dans chaque structure
-- ============================================================
CREATE TABLE IF NOT EXISTS services (
  id                    INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  structure_id          INT UNSIGNED NOT NULL,
  nom                   VARCHAR(100) NOT NULL,
  description           TEXT         NULL,
  duree_consultation_mn INT UNSIGNED NOT NULL DEFAULT 20 COMMENT 'Durée moyenne en minutes',
  nb_medecins_requis    INT UNSIGNED NOT NULL DEFAULT 1 COMMENT 'Minimum pour fonctionner normalement',
  nb_medecins_actuels   INT UNSIGNED NOT NULL DEFAULT 0 COMMENT 'Médecins affectés actuellement',
  est_actif             BOOLEAN NOT NULL DEFAULT TRUE,
  created_at            TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at            TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

  FOREIGN KEY (structure_id) REFERENCES structures_sante(id) ON DELETE CASCADE,

  INDEX idx_structure (structure_id),
  INDEX idx_actif     (est_actif),
  UNIQUE KEY uq_service_structure (structure_id, nom)
) ENGINE=InnoDB COMMENT='Services médicaux disponibles par structure';


-- ============================================================
-- TABLE 5 : DISPONIBILITES
-- Créneaux horaires disponibles pour chaque médecin
-- ============================================================
CREATE TABLE IF NOT EXISTS disponibilites (
  id            INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  medecin_id    INT UNSIGNED NOT NULL,
  structure_id  INT UNSIGNED NOT NULL COMMENT 'Structure où le médecin travaille ce jour-là',
  service_id    INT UNSIGNED NOT NULL,
  date_travail  DATE NOT NULL,
  heure_debut   TIME NOT NULL,
  heure_fin     TIME NOT NULL,
  nb_slots_max  INT UNSIGNED NOT NULL DEFAULT 10 COMMENT 'Nombre de rendez-vous possibles',
  nb_slots_pris INT UNSIGNED NOT NULL DEFAULT 0,
  est_actif     BOOLEAN NOT NULL DEFAULT TRUE,
  created_at    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

  FOREIGN KEY (medecin_id)   REFERENCES medecins(id) ON DELETE CASCADE,
  FOREIGN KEY (structure_id) REFERENCES structures_sante(id) ON DELETE CASCADE,
  FOREIGN KEY (service_id)   REFERENCES services(id) ON DELETE CASCADE,

  INDEX idx_medecin_date (medecin_id, date_travail),
  INDEX idx_structure_date (structure_id, date_travail),
  -- Empêche un médecin d'avoir deux créneaux qui se chevauchent
  UNIQUE KEY uq_medecin_creneau (medecin_id, date_travail, heure_debut)
) ENGINE=InnoDB COMMENT='Créneaux de travail des médecins';


-- ============================================================
-- TABLE 6 : RENDEZ_VOUS
-- Réservations prises par les patients
-- ============================================================
CREATE TABLE IF NOT EXISTS rendez_vous (
  id                INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  patient_id        INT UNSIGNED NOT NULL,
  medecin_id        INT UNSIGNED NOT NULL,
  service_id        INT UNSIGNED NOT NULL,
  disponibilite_id  INT UNSIGNED NOT NULL,
  date_rdv          DATE        NOT NULL,
  heure_rdv         TIME        NOT NULL,
  motif             TEXT        NULL,
  statut            ENUM('en_attente', 'confirme', 'en_cours', 'termine', 'annule_patient', 'annule_medecin', 'absent') NOT NULL DEFAULT 'en_attente',
  notes_medecin     TEXT        NULL COMMENT 'Observations du médecin (après consultation)',
  code_confirmation VARCHAR(10) NOT NULL COMMENT 'Code court envoyé par SMS',
  rappel_envoye     BOOLEAN     NOT NULL DEFAULT FALSE,
  created_at        TIMESTAMP   NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at        TIMESTAMP   NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

  FOREIGN KEY (patient_id)       REFERENCES utilisateurs(id) ON DELETE RESTRICT,
  FOREIGN KEY (medecin_id)       REFERENCES medecins(id) ON DELETE RESTRICT,
  FOREIGN KEY (service_id)       REFERENCES services(id) ON DELETE RESTRICT,
  FOREIGN KEY (disponibilite_id) REFERENCES disponibilites(id) ON DELETE RESTRICT,

  INDEX idx_patient   (patient_id),
  INDEX idx_medecin   (medecin_id),
  INDEX idx_date      (date_rdv),
  INDEX idx_statut    (statut)
) ENGINE=InnoDB COMMENT='Réservations et consultations des patients';


-- ============================================================
-- TABLE 7 : ALERTES
-- Surcharges et déséquilibres détectés automatiquement
-- ============================================================
CREATE TABLE IF NOT EXISTS alertes (
  id               INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  structure_id     INT UNSIGNED NOT NULL,
  type_alerte      ENUM('surcharge_patients', 'manque_medecins', 'service_indisponible', 'pic_saisonnier') NOT NULL,
  service_id       INT UNSIGNED NULL COMMENT 'Service concerné (peut être NULL si alerte globale)',
  priorite         ENUM('faible', 'moyenne', 'haute', 'critique') NOT NULL DEFAULT 'moyenne',
  message          TEXT NOT NULL,
  taux_charge      TINYINT UNSIGNED NULL COMMENT 'Pourcentage de charge au moment de l\'alerte (0-100)',
  est_traitee      BOOLEAN NOT NULL DEFAULT FALSE,
  traitee_par      INT UNSIGNED NULL COMMENT 'Administrateur qui a traité l\'alerte',
  traitee_le       DATETIME NULL,
  action_effectuee TEXT NULL COMMENT 'Description de l\'action corrective',
  created_at       TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

  FOREIGN KEY (structure_id) REFERENCES structures_sante(id) ON DELETE CASCADE,
  FOREIGN KEY (service_id)   REFERENCES services(id) ON DELETE SET NULL,
  FOREIGN KEY (traitee_par)  REFERENCES utilisateurs(id) ON DELETE SET NULL,

  INDEX idx_structure  (structure_id),
  INDEX idx_priorite   (priorite),
  INDEX idx_traitee    (est_traitee),
  INDEX idx_created    (created_at)
) ENGINE=InnoDB COMMENT='Alertes automatiques de surcharge ou manque de médecins';


-- ============================================================
-- TABLE 8 : REDEPLOIS
-- Missions temporaires d'un médecin dans une autre structure
-- ============================================================
CREATE TABLE IF NOT EXISTS redeplois (
  id                       INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  medecin_id               INT UNSIGNED NOT NULL,
  alerte_id                INT UNSIGNED NULL COMMENT 'Alerte à l\'origine de la demande',
  structure_origine_id     INT UNSIGNED NOT NULL COMMENT 'Structure d\'affectation habituelle',
  structure_destination_id INT UNSIGNED NOT NULL COMMENT 'Structure qui accueille le médecin',
  service_destination_id   INT UNSIGNED NULL COMMENT 'Service dans la structure de destination',
  date_debut               DATE         NOT NULL,
  date_fin                 DATE         NOT NULL,
  statut                   ENUM('propose', 'accepte', 'refuse', 'en_cours', 'termine', 'annule') NOT NULL DEFAULT 'propose',
  motif                    TEXT         NOT NULL,
  note_medecin             TEXT         NULL COMMENT 'Commentaire du médecin sur la mission',
  propose_par              INT UNSIGNED NOT NULL COMMENT 'Administrateur qui a proposé le redéploiement',
  created_at               TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at               TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

  FOREIGN KEY (medecin_id)               REFERENCES medecins(id) ON DELETE RESTRICT,
  FOREIGN KEY (alerte_id)                REFERENCES alertes(id) ON DELETE SET NULL,
  FOREIGN KEY (structure_origine_id)     REFERENCES structures_sante(id) ON DELETE RESTRICT,
  FOREIGN KEY (structure_destination_id) REFERENCES structures_sante(id) ON DELETE RESTRICT,
  FOREIGN KEY (service_destination_id)   REFERENCES services(id) ON DELETE SET NULL,
  FOREIGN KEY (propose_par)              REFERENCES utilisateurs(id) ON DELETE RESTRICT,

  -- Empêche deux redéploiements actifs en même temps pour le même médecin
  INDEX idx_medecin_statut (medecin_id, statut),
  INDEX idx_destination    (structure_destination_id),
  INDEX idx_dates          (date_debut, date_fin)
) ENGINE=InnoDB COMMENT='Missions temporaires de médecins entre structures';


-- ============================================================
-- TABLE 9 : NOTIFICATIONS
-- Messages envoyés aux utilisateurs (SMS, email, in-app)
-- ============================================================
CREATE TABLE IF NOT EXISTS notifications (
  id              INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  utilisateur_id  INT UNSIGNED NOT NULL,
  rendez_vous_id  INT UNSIGNED NULL COMMENT 'Lié à un RDV si applicable',
  alerte_id       INT UNSIGNED NULL COMMENT 'Lié à une alerte si applicable',
  type_notif      ENUM('confirmation_rdv', 'rappel_rdv', 'annulation_rdv', 'alerte_surcharge', 'proposition_redeploiement', 'message_admin', 'info_generale') NOT NULL,
  canal           ENUM('sms', 'email', 'push', 'inapp') NOT NULL DEFAULT 'inapp',
  titre           VARCHAR(150) NOT NULL,
  message         TEXT NOT NULL,
  est_lu          BOOLEAN  NOT NULL DEFAULT FALSE,
  est_envoye      BOOLEAN  NOT NULL DEFAULT FALSE,
  envoye_le       DATETIME NULL,
  lu_le           DATETIME NULL,
  created_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

  FOREIGN KEY (utilisateur_id) REFERENCES utilisateurs(id) ON DELETE CASCADE,
  FOREIGN KEY (rendez_vous_id) REFERENCES rendez_vous(id) ON DELETE SET NULL,
  FOREIGN KEY (alerte_id)      REFERENCES alertes(id) ON DELETE SET NULL,

  INDEX idx_utilisateur (utilisateur_id),
  INDEX idx_non_lu      (utilisateur_id, est_lu),
  INDEX idx_type        (type_notif)
) ENGINE=InnoDB COMMENT='Notifications envoyées à tous les utilisateurs';


-- ============================================================
-- TABLE 10 : RAPPORTS
-- Statistiques générées pour les gestionnaires
-- ============================================================
CREATE TABLE IF NOT EXISTS rapports (
  id              INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  genere_par      INT UNSIGNED NOT NULL COMMENT 'Administrateur ayant généré le rapport',
  structure_id    INT UNSIGNED NULL COMMENT 'NULL = rapport national / multi-structures',
  type_rapport    ENUM('activite_journaliere', 'charge_hebdomadaire', 'performance_medecins', 'flux_patients', 'bilan_redeplois', 'statistiques_mensuelles') NOT NULL,
  periode_debut   DATE NOT NULL,
  periode_fin     DATE NOT NULL,
  titre           VARCHAR(200) NOT NULL,
  donnees_json    JSON NOT NULL COMMENT 'Données du rapport au format JSON',
  fichier_pdf     VARCHAR(255) NULL COMMENT 'Chemin vers le PDF généré',
  created_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

  FOREIGN KEY (genere_par)   REFERENCES utilisateurs(id) ON DELETE RESTRICT,
  FOREIGN KEY (structure_id) REFERENCES structures_sante(id) ON DELETE SET NULL,

  INDEX idx_structure (structure_id),
  INDEX idx_type      (type_rapport),
  INDEX idx_periode   (periode_debut, periode_fin)
) ENGINE=InnoDB COMMENT='Rapports statistiques générés par les administrateurs';


-- ============================================================
-- VUES UTILES (pour simplifier les requêtes courantes)
-- ============================================================

-- Vue : Charge en temps réel par structure
CREATE OR REPLACE VIEW vue_charge_structures AS
SELECT
  s.id,
  s.nom,
  s.region,
  s.ville,
  s.type_structure,
  s.capacite_journaliere,
  s.charge_actuelle,
  ROUND((s.charge_actuelle / s.capacite_journaliere) * 100, 1) AS taux_charge_pct,
  CASE
    WHEN (s.charge_actuelle / s.capacite_journaliere) >= 0.90 THEN 'critique'
    WHEN (s.charge_actuelle / s.capacite_journaliere) >= 0.75 THEN 'haute'
    WHEN (s.charge_actuelle / s.capacite_journaliere) >= 0.50 THEN 'moyenne'
    ELSE 'normale'
  END AS niveau_charge,
  (SELECT COUNT(*) FROM medecins m WHERE m.structure_id = s.id AND m.disponibilite = 'disponible') AS medecins_disponibles,
  (SELECT COUNT(*) FROM medecins m WHERE m.structure_id = s.id) AS total_medecins
FROM structures_sante s
WHERE s.statut = 'actif';

-- Vue : Rendez-vous du jour avec détails complets
CREATE OR REPLACE VIEW vue_rdv_aujourd_hui AS
SELECT
  r.id,
  r.heure_rdv,
  r.statut,
  r.motif,
  CONCAT(u_p.prenom, ' ', u_p.nom) AS nom_patient,
  u_p.telephone                     AS tel_patient,
  CONCAT(u_m.prenom, ' ', u_m.nom) AS nom_medecin,
  md.specialite,
  sv.nom                            AS service,
  st.nom                            AS structure
FROM rendez_vous r
JOIN utilisateurs  u_p ON r.patient_id = u_p.id
JOIN medecins      md  ON r.medecin_id = md.id
JOIN utilisateurs  u_m ON md.utilisateur_id = u_m.id
JOIN services      sv  ON r.service_id = sv.id
JOIN structures_sante st ON sv.structure_id = st.id
WHERE r.date_rdv = CURDATE();

-- Vue : Médecins disponibles pour redéploiement
CREATE OR REPLACE VIEW vue_medecins_redeployables AS
SELECT
  md.id AS medecin_id,
  CONCAT(u.prenom, ' ', u.nom) AS nom_complet,
  u.telephone,
  md.specialite,
  md.grade,
  md.disponibilite,
  md.rayon_deploiement_km,
  st.nom    AS structure_actuelle,
  st.region AS region_actuelle,
  st.latitude,
  st.longitude
FROM medecins md
JOIN utilisateurs    u  ON md.utilisateur_id = u.id
JOIN structures_sante st ON md.structure_id = st.id
WHERE md.disponibilite IN ('disponible')
  AND md.peut_etre_redeploye = TRUE
  AND u.est_actif = TRUE;


-- ============================================================
-- DONNÉES DE TEST (Sénégal — données fictives)
-- ============================================================

-- Administrateur principal
-- Mot de passe de test : Sunu2025!
INSERT INTO utilisateurs (nom, prenom, email, telephone, mot_de_passe, role, ville) VALUES
('FALL', 'Mangoné', 'admin@plateforme-med.sn', '+221771234567', '$2b$12$t0UCWUx1ZCWBafzuiCUvJ.oMRBitGk/4l.Mem0sYR59ldd.ByJBt6', 'administrateur', 'Dakar');

-- Structures de santé
INSERT INTO structures_sante (nom, type_structure, adresse, ville, region, telephone, latitude, longitude, capacite_journaliere, seuil_alerte) VALUES
('Hôpital Principal de Dakar',    'hopital',        'Avenue Nelson Mandela, Dakar',       'Dakar',     'Dakar',     '+221338221234', 14.6928, -17.4467, 200, 160),
('Hôpital Aristide Le Dantec',    'hopital',        'Avenue Pasteur, Dakar',              'Dakar',     'Dakar',     '+221338223456', 14.6880, -17.4398, 180, 140),
('Centre de Santé de Pikine',     'centre_sante',   'Route de Pikine, Pikine',            'Pikine',    'Dakar',     '+221338451234', 14.7547, -17.3929, 80,  65),
('Hôpital Régional de Thiès',     'hopital',        'Boulevard de Gaulle, Thiès',         'Thiès',     'Thiès',     '+221339711234', 14.7886, -16.9256, 120, 90),
('Centre de Santé de Ziguinchor', 'centre_sante',   'Rue du Commerce, Ziguinchor',        'Ziguinchor','Ziguinchor','+221335910000', 12.5606, -16.2728, 60,  45),
('Poste de Santé de Touba',       'poste_sante',    'Quartier Darou Khoudoss, Touba',     'Touba',     'Diourbel',  '+221336810000', 14.8585, -15.8835, 40,  30);

-- Services par structure
INSERT INTO services (structure_id, nom, duree_consultation_mn, nb_medecins_requis) VALUES
(1, 'Médecine générale', 20, 5),
(1, 'Cardiologie',       30, 2),
(1, 'Pédiatrie',         25, 3),
(1, 'Urgences',          15, 4),
(2, 'Médecine générale', 20, 4),
(2, 'Dermatologie',      25, 2),
(2, 'Ophtalmologie',     30, 2),
(3, 'Médecine générale', 20, 2),
(3, 'Pédiatrie',         25, 1),
(4, 'Médecine générale', 20, 3),
(4, 'Chirurgie générale',45, 2),
(5, 'Médecine générale', 20, 2),
(6, 'Médecine générale', 20, 1);

-- Médecins (utilisateurs + profil médecin)
-- Mot de passe de test : Sunu2025!
INSERT INTO utilisateurs (nom, prenom, email, telephone, mot_de_passe, role, ville) VALUES
('DIALLO',  'Amadou',  'a.diallo@med.sn',  '+221771111111', '$2b$12$zX4Pgs/cRqcGVJqiH1ooYO0QMt.Zqw30LYBR0n8Tefm./jquvu5tK', 'medecin', 'Dakar'),
('NDIAYE',  'Fatou',   'f.ndiaye@med.sn',  '+221772222222', '$2b$12$jOpBn6z9OBuJEHjGUYLWie6hQXJsX4Fl7nj3FtDdYRFtiMYwJfokm', 'medecin', 'Dakar'),
('SOW',     'Moussa',  'm.sow@med.sn',     '+221773333333', '$2b$12$pS57M4f278aIJXASEi98W.pkfFMUgye.33NTq0F/u/CBnlNw1wJ3e', 'medecin', 'Thiès'),
('BADJI',   'Aïssatou','a.badji@med.sn',   '+221774444444', '$2b$12$wkutUfZV/l1j2OnSifOileX2VrkSoryTqR31UMPggFs48QAB2ti6i', 'medecin', 'Ziguinchor'),
('MBAYE',   'Ibrahima','i.mbaye@med.sn',   '+221775555555', '$2b$12$u.11TWJElEFJ.TMfqQLla.4QhfFIKP74IIlkaEs3jDLswifFDW9OS', 'medecin', 'Dakar');

INSERT INTO medecins (utilisateur_id, structure_id, specialite, numero_ordre, grade, disponibilite) VALUES
(2, 1, 'Cardiologie',      'SN-CNOM-2019-001', 'specialiste',  'disponible'),
(3, 1, 'Médecine générale','SN-CNOM-2021-042', 'generaliste',  'en_consultation'),
(4, 4, 'Médecine générale','SN-CNOM-2020-115', 'generaliste',  'disponible'),
(5, 5, 'Pédiatrie',        'SN-CNOM-2018-088', 'specialiste',  'disponible'),
(6, 2, 'Médecine générale','SN-CNOM-2022-203', 'interne',      'disponible');

-- Patients
-- Mot de passe de test : Sunu2025!
INSERT INTO utilisateurs (nom, prenom, email, telephone, mot_de_passe, role, ville, date_naissance, sexe) VALUES
('SARR',    'Mariama', 'm.sarr@gmail.com',   '+221770000001', '$2b$12$LQNyvzWk4oVt7WM4rwrrzeXTZcmdtH.353.1Wz0m3JkCQ0aEnCDam', 'patient', 'Dakar',     '1990-05-12', 'feminin'),
('THIAM',   'Cheikh',  'c.thiam@gmail.com',  '+221770000002', '$2b$12$4Eb9tOxNheMiPriHJLfYEuOV1N6UtVCxZ5ZHYRDV6k2NOc83rt5zi', 'patient', 'Pikine',    '1985-11-23', 'masculin'),
('GUEYE',   'Rokhaya', 'r.gueye@gmail.com',  '+221770000003', '$2b$12$PNBiM7VnpFQyRWqGXJsMSeYHHSyZPfvXZj3ezU6ATsFU6FqUk7R7m', 'patient', 'Dakar',     '2000-03-07', 'feminin'),
('KANE',    'Abdoulaye','a.kane@gmail.com',  '+221770000004', '$2b$12$9yGt1n4MmQ0NL3ZpQSkgQujL1zXVXPX6thDELS6adNOq6o/DI50o.', 'patient', 'Thiès',     '1975-08-30', 'masculin');

-- ============================================================
-- PROCÉDURES STOCKÉES
-- ============================================================

DELIMITER $$

-- Procédure : calculer la charge d'une structure et créer une alerte si nécessaire
CREATE PROCEDURE verifier_charge_structure(IN p_structure_id INT UNSIGNED)
BEGIN
  DECLARE v_charge    INT UNSIGNED;
  DECLARE v_capacite  INT UNSIGNED;
  DECLARE v_seuil     INT UNSIGNED;
  DECLARE v_taux      DECIMAL(5,2);

  SELECT charge_actuelle, capacite_journaliere, seuil_alerte
  INTO   v_charge, v_capacite, v_seuil
  FROM   structures_sante
  WHERE  id = p_structure_id;

  SET v_taux = (v_charge / v_capacite) * 100;

  -- Créer une alerte si la charge dépasse le seuil et qu'il n'en existe pas déjà une non traitée
  IF v_charge >= v_seuil AND NOT EXISTS (
    SELECT 1 FROM alertes
    WHERE structure_id = p_structure_id
      AND type_alerte  = 'surcharge_patients'
      AND est_traitee  = FALSE
      AND created_at   > NOW() - INTERVAL 2 HOUR
  ) THEN
    INSERT INTO alertes (structure_id, type_alerte, priorite, message, taux_charge)
    VALUES (
      p_structure_id,
      'surcharge_patients',
      CASE
        WHEN v_taux >= 95 THEN 'critique'
        WHEN v_taux >= 85 THEN 'haute'
        ELSE 'moyenne'
      END,
      CONCAT('La structure a atteint ', ROUND(v_taux, 0), '% de sa capacité journalière (', v_charge, '/', v_capacite, ' patients).'),
      ROUND(v_taux)
    );
  END IF;
END$$

-- Procédure : créer un rendez-vous et décrémenter le slot de disponibilité
CREATE PROCEDURE creer_rendez_vous(
  IN p_patient_id       INT UNSIGNED,
  IN p_disponibilite_id INT UNSIGNED,
  IN p_motif            TEXT,
  OUT p_rdv_id          INT UNSIGNED,
  OUT p_code            VARCHAR(10)
)
BEGIN
  DECLARE v_medecin_id  INT UNSIGNED;
  DECLARE v_service_id  INT UNSIGNED;
  DECLARE v_date        DATE;
  DECLARE v_heure       TIME;
  DECLARE v_slots_pris  INT UNSIGNED;
  DECLARE v_slots_max   INT UNSIGNED;

  SELECT medecin_id, service_id, date_travail, heure_debut, nb_slots_pris, nb_slots_max
  INTO   v_medecin_id, v_service_id, v_date, v_heure, v_slots_pris, v_slots_max
  FROM   disponibilites
  WHERE  id = p_disponibilite_id AND est_actif = TRUE
  FOR UPDATE;

  IF v_slots_pris >= v_slots_max THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Créneau complet, veuillez choisir un autre.';
  END IF;

  -- Générer un code de confirmation à 6 chiffres
  SET p_code = LPAD(FLOOR(RAND() * 999999), 6, '0');

  INSERT INTO rendez_vous (patient_id, medecin_id, service_id, disponibilite_id, date_rdv, heure_rdv, motif, code_confirmation)
  VALUES (p_patient_id, v_medecin_id, v_service_id, p_disponibilite_id, v_date, v_heure, p_motif, p_code);

  SET p_rdv_id = LAST_INSERT_ID();

  UPDATE disponibilites SET nb_slots_pris = nb_slots_pris + 1 WHERE id = p_disponibilite_id;
END$$

DELIMITER ;


-- ============================================================
-- INDEX COMPOSITES SUPPLÉMENTAIRES (performances)
-- ============================================================
-- Pour récupérer rapidement les RDV par médecin à une date donnée
CREATE INDEX idx_rdv_medecin_date ON rendez_vous (medecin_id, date_rdv, statut);
-- Pour récupérer les alertes actives par priorité
CREATE INDEX idx_alertes_actives  ON alertes (est_traitee, priorite, created_at);


SET FOREIGN_KEY_CHECKS = 1;

-- ============================================================
-- DONNÉES DE TEST SUPPLÉMENTAIRES
-- ============================================================

-- Charge actuelle des structures (pour le dashboard)
UPDATE structures_sante SET charge_actuelle = 176 WHERE id = 1; -- HPD 88%
UPDATE structures_sante SET charge_actuelle = 128 WHERE id = 2; -- Le Dantec 71%
UPDATE structures_sante SET charge_actuelle = 50  WHERE id = 3; -- Pikine 62%
UPDATE structures_sante SET charge_actuelle = 41  WHERE id = 4; -- Thiès 34%
UPDATE structures_sante SET charge_actuelle = 25  WHERE id = 5; -- Ziguinchor 41%
UPDATE structures_sante SET charge_actuelle = 7   WHERE id = 6; -- Touba 18%

-- Disponibilités pour les 14 prochains jours (médecin 1 = Amadou Diallo, Cardio, HPD)
INSERT INTO disponibilites (medecin_id, structure_id, service_id, date_travail, heure_debut, heure_fin, nb_slots_max) VALUES
(1, 1, 2, DATE_ADD(CURDATE(), INTERVAL 1 DAY),  '08:00:00', '12:00:00', 8),
(1, 1, 2, DATE_ADD(CURDATE(), INTERVAL 2 DAY),  '08:00:00', '12:00:00', 8),
(1, 1, 2, DATE_ADD(CURDATE(), INTERVAL 3 DAY),  '08:00:00', '12:00:00', 8),
(1, 1, 2, DATE_ADD(CURDATE(), INTERVAL 4 DAY),  '14:00:00', '18:00:00', 8),
(1, 1, 2, DATE_ADD(CURDATE(), INTERVAL 7 DAY),  '08:00:00', '12:00:00', 8),
(1, 1, 2, DATE_ADD(CURDATE(), INTERVAL 8 DAY),  '08:00:00', '12:00:00', 8),
(1, 1, 2, DATE_ADD(CURDATE(), INTERVAL 9 DAY),  '14:00:00', '18:00:00', 8),
(1, 1, 2, DATE_ADD(CURDATE(), INTERVAL 10 DAY), '08:00:00', '12:00:00', 8),
-- Médecin 2 = Fatou Ndiaye, Médecine générale, HPD
(2, 1, 1, DATE_ADD(CURDATE(), INTERVAL 1 DAY),  '08:00:00', '12:00:00', 10),
(2, 1, 1, DATE_ADD(CURDATE(), INTERVAL 2 DAY),  '08:00:00', '12:00:00', 10),
(2, 1, 1, DATE_ADD(CURDATE(), INTERVAL 3 DAY),  '14:00:00', '18:00:00', 10),
(2, 1, 1, DATE_ADD(CURDATE(), INTERVAL 5 DAY),  '08:00:00', '12:00:00', 10),
(2, 1, 1, DATE_ADD(CURDATE(), INTERVAL 6 DAY),  '08:00:00', '12:00:00', 10),
-- Médecin 3 = Moussa Sow, Médecine générale, Thiès
(3, 4, 10, DATE_ADD(CURDATE(), INTERVAL 1 DAY), '08:00:00', '12:00:00', 8),
(3, 4, 10, DATE_ADD(CURDATE(), INTERVAL 2 DAY), '08:00:00', '12:00:00', 8),
(3, 4, 10, DATE_ADD(CURDATE(), INTERVAL 3 DAY), '14:00:00', '18:00:00', 8),
(3, 4, 10, DATE_ADD(CURDATE(), INTERVAL 7 DAY), '08:00:00', '12:00:00', 8),
-- Médecin 4 = Aïssatou Badji, Pédiatrie, Ziguinchor
(4, 5, 12, DATE_ADD(CURDATE(), INTERVAL 1 DAY), '08:00:00', '12:00:00', 6),
(4, 5, 12, DATE_ADD(CURDATE(), INTERVAL 2 DAY), '08:00:00', '12:00:00', 6),
(4, 5, 12, DATE_ADD(CURDATE(), INTERVAL 4 DAY), '14:00:00', '18:00:00', 6),
-- Médecin 5 = Ibrahima Mbaye, Médecine générale, Le Dantec
(5, 2, 5, DATE_ADD(CURDATE(), INTERVAL 1 DAY),  '08:00:00', '12:00:00', 10),
(5, 2, 5, DATE_ADD(CURDATE(), INTERVAL 2 DAY),  '14:00:00', '18:00:00', 10),
(5, 2, 5, DATE_ADD(CURDATE(), INTERVAL 3 DAY),  '08:00:00', '12:00:00', 10);

-- Alertes actives de test
INSERT INTO alertes (structure_id, type_alerte, priorite, message, taux_charge) VALUES
(1, 'surcharge_patients', 'critique', 'La structure a atteint 88% de sa capacité journalière (176/200 patients).', 88),
(3, 'manque_medecins',    'haute',    'Pédiatrie : 1 médecin actif pour 2 requis. Charge à 62%.', 62),
(2, 'surcharge_patients', 'moyenne',  'Affluence prévue en hausse. Charge actuelle à 71%.', 71);

-- ============================================================
-- FIN DU FICHIER — SUNU KIRAY
-- ============================================================
