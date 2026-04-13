-- Charges réelles des structures
UPDATE structures_sante SET charge_actuelle = 176 WHERE id = 1;
UPDATE structures_sante SET charge_actuelle = 128 WHERE id = 2;
UPDATE structures_sante SET charge_actuelle = 50  WHERE id = 3;
UPDATE structures_sante SET charge_actuelle = 41  WHERE id = 4;
UPDATE structures_sante SET charge_actuelle = 25  WHERE id = 5;
UPDATE structures_sante SET charge_actuelle = 7   WHERE id = 6;

-- Alertes actives
INSERT IGNORE INTO alertes (structure_id, type_alerte, priorite, message, taux_charge) VALUES
(1, 'surcharge_patients', 'critique', 'La structure a atteint 88% de sa capacité (176/200 patients).', 88),
(3, 'manque_medecins',    'haute',    'Pédiatrie : 1 médecin actif pour 2 requis. Charge à 62%.', 62),
(2, 'surcharge_patients', 'moyenne',  'Affluence en hausse. Charge actuelle à 71%.', 71);

-- Disponibilités complètes pour les 14 prochains jours
-- Médecin 1 (Amadou Diallo) - Cardiologie - HPD (structure 1, service 2)
INSERT IGNORE INTO disponibilites (medecin_id, structure_id, service_id, date_travail, heure_debut, heure_fin, nb_slots_max) VALUES
(1, 1, 2, DATE_ADD(CURDATE(), INTERVAL 1 DAY),  '08:00:00', '12:00:00', 8),
(1, 1, 2, DATE_ADD(CURDATE(), INTERVAL 2 DAY),  '08:00:00', '12:00:00', 8),
(1, 1, 2, DATE_ADD(CURDATE(), INTERVAL 3 DAY),  '14:00:00', '18:00:00', 8),
(1, 1, 2, DATE_ADD(CURDATE(), INTERVAL 5 DAY),  '08:00:00', '12:00:00', 8),
(1, 1, 2, DATE_ADD(CURDATE(), INTERVAL 7 DAY),  '08:00:00', '12:00:00', 8),
(1, 1, 2, DATE_ADD(CURDATE(), INTERVAL 8 DAY),  '14:00:00', '18:00:00', 8),
(1, 1, 2, DATE_ADD(CURDATE(), INTERVAL 10 DAY), '08:00:00', '12:00:00', 8),
(1, 1, 2, DATE_ADD(CURDATE(), INTERVAL 12 DAY), '08:00:00', '12:00:00', 8),
-- Médecin 2 (Fatou Ndiaye) - Médecine générale - HPD (structure 1, service 1)
(2, 1, 1, DATE_ADD(CURDATE(), INTERVAL 1 DAY),  '08:00:00', '12:00:00', 10),
(2, 1, 1, DATE_ADD(CURDATE(), INTERVAL 2 DAY),  '14:00:00', '18:00:00', 10),
(2, 1, 1, DATE_ADD(CURDATE(), INTERVAL 3 DAY),  '08:00:00', '12:00:00', 10),
(2, 1, 1, DATE_ADD(CURDATE(), INTERVAL 5 DAY),  '14:00:00', '18:00:00', 10),
(2, 1, 1, DATE_ADD(CURDATE(), INTERVAL 7 DAY),  '08:00:00', '12:00:00', 10),
(2, 1, 1, DATE_ADD(CURDATE(), INTERVAL 9 DAY),  '14:00:00', '18:00:00', 10),
-- Médecin 3 (Moussa Sow) - Médecine générale - Thiès (structure 4, service 10)
(3, 4, 10, DATE_ADD(CURDATE(), INTERVAL 1 DAY), '08:00:00', '12:00:00', 8),
(3, 4, 10, DATE_ADD(CURDATE(), INTERVAL 2 DAY), '14:00:00', '18:00:00', 8),
(3, 4, 10, DATE_ADD(CURDATE(), INTERVAL 4 DAY), '08:00:00', '12:00:00', 8),
(3, 4, 10, DATE_ADD(CURDATE(), INTERVAL 6 DAY), '08:00:00', '12:00:00', 8),
(3, 4, 10, DATE_ADD(CURDATE(), INTERVAL 8 DAY), '14:00:00', '18:00:00', 8),
(3, 4, 10, DATE_ADD(CURDATE(), INTERVAL 11 DAY),'08:00:00', '12:00:00', 8),
-- Médecin 4 (Aïssatou Badji) - Pédiatrie - Ziguinchor (structure 5, service 12)
(4, 5, 12, DATE_ADD(CURDATE(), INTERVAL 1 DAY), '08:00:00', '12:00:00', 6),
(4, 5, 12, DATE_ADD(CURDATE(), INTERVAL 3 DAY), '14:00:00', '18:00:00', 6),
(4, 5, 12, DATE_ADD(CURDATE(), INTERVAL 5 DAY), '08:00:00', '12:00:00', 6),
(4, 5, 12, DATE_ADD(CURDATE(), INTERVAL 7 DAY), '14:00:00', '18:00:00', 6),
(4, 5, 12, DATE_ADD(CURDATE(), INTERVAL 10 DAY),'08:00:00', '12:00:00', 6),
-- Médecin 5 (Ibrahima Mbaye) - Médecine générale - Le Dantec (structure 2, service 5)
(5, 2, 5,  DATE_ADD(CURDATE(), INTERVAL 1 DAY), '08:00:00', '12:00:00', 10),
(5, 2, 5,  DATE_ADD(CURDATE(), INTERVAL 2 DAY), '14:00:00', '18:00:00', 10),
(5, 2, 5,  DATE_ADD(CURDATE(), INTERVAL 4 DAY), '08:00:00', '12:00:00', 10),
(5, 2, 5,  DATE_ADD(CURDATE(), INTERVAL 6 DAY), '14:00:00', '18:00:00', 10),
(5, 2, 5,  DATE_ADD(CURDATE(), INTERVAL 9 DAY), '08:00:00', '12:00:00', 10),
(5, 2, 5,  DATE_ADD(CURDATE(), INTERVAL 13 DAY),'14:00:00', '18:00:00', 10);
