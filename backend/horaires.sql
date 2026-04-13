-- ============================================================
--  SUNU KIRAY — Horaires hebdomadaires des médecins
--  Permet la génération automatique des disponibilités
-- ============================================================

USE sunu_kiray;

-- Table des horaires récurrents par médecin
CREATE TABLE IF NOT EXISTS horaires_medecins (
  id           INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  medecin_id   INT UNSIGNED NOT NULL,
  structure_id INT UNSIGNED NOT NULL,
  service_id   INT UNSIGNED NOT NULL,
  jour_semaine TINYINT UNSIGNED NOT NULL COMMENT '0=Lundi, 1=Mardi, ..., 5=Samedi',
  heure_debut  TIME NOT NULL,
  heure_fin    TIME NOT NULL,
  nb_slots     INT UNSIGNED NOT NULL DEFAULT 10,
  est_actif    BOOLEAN NOT NULL DEFAULT TRUE,
  created_at   TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

  FOREIGN KEY (medecin_id)   REFERENCES medecins(id) ON DELETE CASCADE,
  FOREIGN KEY (structure_id) REFERENCES structures_sante(id) ON DELETE CASCADE,
  FOREIGN KEY (service_id)   REFERENCES services(id) ON DELETE CASCADE,

  UNIQUE KEY uq_horaire (medecin_id, service_id, jour_semaine, heure_debut)
) ENGINE=InnoDB COMMENT='Horaires hebdomadaires récurrents des médecins';

-- ============================================================
-- Horaires de base pour tous les médecins
-- Lundi(0) à Vendredi(4) : matin + après-midi
-- Samedi(5) : matin seulement
-- ============================================================

-- Médecin 1 : Amadou Diallo - Cardiologie - HPD
INSERT IGNORE INTO horaires_medecins (medecin_id, structure_id, service_id, jour_semaine, heure_debut, heure_fin, nb_slots) VALUES
(1, 1, 2, 0, '08:00:00', '12:00:00', 8), (1, 1, 2, 0, '14:00:00', '18:00:00', 8),
(1, 1, 2, 1, '08:00:00', '12:00:00', 8), (1, 1, 2, 1, '14:00:00', '18:00:00', 8),
(1, 1, 2, 2, '08:00:00', '12:00:00', 8), (1, 1, 2, 2, '14:00:00', '18:00:00', 8),
(1, 1, 2, 3, '08:00:00', '12:00:00', 8), (1, 1, 2, 3, '14:00:00', '18:00:00', 8),
(1, 1, 2, 4, '08:00:00', '12:00:00', 8), (1, 1, 2, 4, '14:00:00', '18:00:00', 8),
(1, 1, 2, 5, '08:00:00', '12:00:00', 8);

-- Médecin 2 : Fatou Ndiaye - Médecine générale - HPD
INSERT IGNORE INTO horaires_medecins (medecin_id, structure_id, service_id, jour_semaine, heure_debut, heure_fin, nb_slots) VALUES
(2, 1, 1, 0, '08:00:00', '12:00:00', 10), (2, 1, 1, 0, '14:00:00', '18:00:00', 10),
(2, 1, 1, 1, '08:00:00', '12:00:00', 10), (2, 1, 1, 1, '14:00:00', '18:00:00', 10),
(2, 1, 1, 2, '08:00:00', '12:00:00', 10), (2, 1, 1, 2, '14:00:00', '18:00:00', 10),
(2, 1, 1, 3, '08:00:00', '12:00:00', 10), (2, 1, 1, 3, '14:00:00', '18:00:00', 10),
(2, 1, 1, 4, '08:00:00', '12:00:00', 10), (2, 1, 1, 4, '14:00:00', '18:00:00', 10),
(2, 1, 1, 5, '08:00:00', '12:00:00', 10);

-- Médecin 3 : Moussa Sow - Médecine générale - Thiès
INSERT IGNORE INTO horaires_medecins (medecin_id, structure_id, service_id, jour_semaine, heure_debut, heure_fin, nb_slots) VALUES
(3, 4, 10, 0, '08:00:00', '12:00:00', 8), (3, 4, 10, 0, '14:00:00', '18:00:00', 8),
(3, 4, 10, 1, '08:00:00', '12:00:00', 8), (3, 4, 10, 1, '14:00:00', '18:00:00', 8),
(3, 4, 10, 2, '08:00:00', '12:00:00', 8), (3, 4, 10, 2, '14:00:00', '18:00:00', 8),
(3, 4, 10, 3, '08:00:00', '12:00:00', 8), (3, 4, 10, 3, '14:00:00', '18:00:00', 8),
(3, 4, 10, 4, '08:00:00', '12:00:00', 8), (3, 4, 10, 4, '14:00:00', '18:00:00', 8),
(3, 4, 10, 5, '08:00:00', '12:00:00', 8);

-- Médecin 4 : Aïssatou Badji - Pédiatrie - Ziguinchor
INSERT IGNORE INTO horaires_medecins (medecin_id, structure_id, service_id, jour_semaine, heure_debut, heure_fin, nb_slots) VALUES
(4, 5, 12, 0, '08:00:00', '12:00:00', 6), (4, 5, 12, 0, '14:00:00', '18:00:00', 6),
(4, 5, 12, 1, '08:00:00', '12:00:00', 6), (4, 5, 12, 1, '14:00:00', '18:00:00', 6),
(4, 5, 12, 2, '08:00:00', '12:00:00', 6), (4, 5, 12, 2, '14:00:00', '18:00:00', 6),
(4, 5, 12, 3, '08:00:00', '12:00:00', 6), (4, 5, 12, 3, '14:00:00', '18:00:00', 6),
(4, 5, 12, 4, '08:00:00', '12:00:00', 6), (4, 5, 12, 4, '14:00:00', '18:00:00', 6),
(4, 5, 12, 5, '08:00:00', '12:00:00', 6);

-- Médecin 5 : Ibrahima Mbaye - Médecine générale - Le Dantec
INSERT IGNORE INTO horaires_medecins (medecin_id, structure_id, service_id, jour_semaine, heure_debut, heure_fin, nb_slots) VALUES
(5, 2, 5, 0, '08:00:00', '12:00:00', 10), (5, 2, 5, 0, '14:00:00', '18:00:00', 10),
(5, 2, 5, 1, '08:00:00', '12:00:00', 10), (5, 2, 5, 1, '14:00:00', '18:00:00', 10),
(5, 2, 5, 2, '08:00:00', '12:00:00', 10), (5, 2, 5, 2, '14:00:00', '18:00:00', 10),
(5, 2, 5, 3, '08:00:00', '12:00:00', 10), (5, 2, 5, 3, '14:00:00', '18:00:00', 10),
(5, 2, 5, 4, '08:00:00', '12:00:00', 10), (5, 2, 5, 4, '14:00:00', '18:00:00', 10),
(5, 2, 5, 5, '08:00:00', '12:00:00', 10);

-- Médecins Pikine et Touba (IDs 6 et 7 créés par add_medecins.sql)
-- On récupère leurs IDs dynamiquement
INSERT IGNORE INTO horaires_medecins (medecin_id, structure_id, service_id, jour_semaine, heure_debut, heure_fin, nb_slots)
SELECT m.id, m.structure_id, sv.id, j.jour, '08:00:00', '12:00:00', 10
FROM medecins m
JOIN services sv ON sv.structure_id = m.structure_id AND sv.est_actif = 1
JOIN (SELECT 0 jour UNION SELECT 1 UNION SELECT 2 UNION SELECT 3 UNION SELECT 4 UNION SELECT 5) j
WHERE m.structure_id IN (3, 6);

INSERT IGNORE INTO horaires_medecins (medecin_id, structure_id, service_id, jour_semaine, heure_debut, heure_fin, nb_slots)
SELECT m.id, m.structure_id, sv.id, j.jour, '14:00:00', '18:00:00', 10
FROM medecins m
JOIN services sv ON sv.structure_id = m.structure_id AND sv.est_actif = 1
JOIN (SELECT 0 jour UNION SELECT 1 UNION SELECT 2 UNION SELECT 3 UNION SELECT 4) j
WHERE m.structure_id IN (3, 6);

-- ============================================================
-- Procédure : générer les disponibilités depuis les horaires
-- Appeler avec : CALL generer_disponibilites(30);
-- ============================================================

DROP PROCEDURE IF EXISTS generer_disponibilites;

DELIMITER $

CREATE PROCEDURE generer_disponibilites(IN nb_jours INT)
BEGIN
  DECLARE i INT DEFAULT 1;
  DECLARE target_date DATE;
  DECLARE dow TINYINT; -- 0=Lundi ... 6=Dimanche

  WHILE i <= nb_jours DO
    SET target_date = DATE_ADD(CURDATE(), INTERVAL i DAY);
    -- MySQL DAYOFWEEK : 1=Dim, 2=Lun, ..., 7=Sam → on convertit en 0=Lun..5=Sam
    SET dow = MOD(DAYOFWEEK(target_date) + 5, 7);

    -- Insérer les créneaux manquants pour ce jour
    INSERT IGNORE INTO disponibilites
      (medecin_id, structure_id, service_id, date_travail, heure_debut, heure_fin, nb_slots_max)
    SELECT
      h.medecin_id, h.structure_id, h.service_id,
      target_date, h.heure_debut, h.heure_fin, h.nb_slots
    FROM horaires_medecins h
    WHERE h.jour_semaine = dow
      AND h.est_actif = TRUE
      AND dow < 6; -- Pas le dimanche

    SET i = i + 1;
  END WHILE;

  SELECT ROW_COUNT() AS creneaux_generes;
END$

DELIMITER ;

-- Générer immédiatement les 30 prochains jours
CALL generer_disponibilites(30);
