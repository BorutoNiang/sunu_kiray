-- Ajouter des médecins pour les structures sans médecin (Pikine id=3, Touba id=6)
INSERT INTO utilisateurs (nom, prenom, email, telephone, mot_de_passe, role, ville) VALUES
('DIOP',  'Cheikh',  'c.diop@med.sn',  '+221776666666', '$2b$12$placeholder', 'medecin', 'Pikine'),
('FALL',  'Aminata', 'a.fall@med.sn',  '+221777777777', '$2b$12$placeholder', 'medecin', 'Touba');

INSERT INTO medecins (utilisateur_id, structure_id, specialite, numero_ordre, grade, disponibilite) VALUES
((SELECT id FROM utilisateurs WHERE email='c.diop@med.sn'), 3, 'Médecine générale', 'SN-CNOM-2023-301', 'generaliste', 'disponible'),
((SELECT id FROM utilisateurs WHERE email='a.fall@med.sn'), 6, 'Médecine générale', 'SN-CNOM-2023-302', 'generaliste', 'disponible');
