# RAPPORT DE PROJET PPP
## Sunu Kiray — Plateforme Numérique de Santé au Sénégal

---

**Établissement :** École Supérieure Polytechnique (ESP) — UCAD  
**Filière :** DIC 1 / DGI  
**Encadrant :** Dr Mangoné FALL  
**Année académique :** 2025-2026  
**Auteur :** Abdou NIANG  
**Dépôt GitHub :** https://github.com/BorutoNiang/sunu_kiray

---

## TABLE DES MATIÈRES

1. Contexte et problématique
2. Objectifs du projet
3. Démarche méthodologique
4. Technologies et outils utilisés
5. Architecture de la solution
6. Conception et modélisation
7. Développement — Fonctionnalités réalisées
8. Tests et validation
9. Résultats et démonstration
10. Difficultés rencontrées et solutions
11. Perspectives d'amélioration
12. Conclusion

---

## 1. CONTEXTE ET PROBLÉMATIQUE

### Contexte général

Le système de santé sénégalais fait face à des défis structurels majeurs : les structures de santé publiques sont souvent surchargées, les patients attendent plusieurs heures avant d'être pris en charge, et la répartition des ressources médicales (médecins, équipements) est inégale entre les régions.

### Problèmes identifiés

- **Longues files d'attente** dans les hôpitaux publics, notamment à Dakar
- **Absence de système de prise de rendez-vous en ligne** accessible au grand public
- **Manque de visibilité** sur la disponibilité des médecins et la charge des structures
- **Redéploiement manuel et réactif** des ressources médicales, sans anticipation
- **Absence de données centralisées** pour les administrateurs de santé

### Chiffres clés

- Plus de **14 régions** au Sénégal avec des disparités d'accès aux soins
- Temps d'attente moyen dans les hôpitaux publics : **2 à 4 heures**
- Taux de pénétration mobile au Sénégal : **plus de 100%** (opportunité numérique)

---

## 2. OBJECTIFS DU PROJET

### Objectif général

Développer une plateforme numérique permettant d'optimiser la gestion des rendez-vous médicaux et le redéploiement des ressources de santé au Sénégal.

### Objectifs spécifiques

1. Permettre aux patients de **prendre des rendez-vous en ligne** depuis leur téléphone
2. Donner aux médecins une **vue en temps réel** de leur planning
3. Fournir aux administrateurs un **tableau de bord centralisé** pour piloter les ressources
4. Automatiser la **détection des surcharges** et suggérer des redéploiements
5. Réduire le temps d'attente des patients de **60%**

---

## 3. DÉMARCHE MÉTHODOLOGIQUE

### Approche adoptée : Développement Agile (Scrum simplifié)

Le projet a été conduit en **sprints de 2 semaines**, avec des livraisons incrémentales et des ajustements continus basés sur les retours.

### Étapes du projet

#### Phase 1 — Analyse (Semaine 1-2)
- Étude du contexte sanitaire sénégalais
- Identification des acteurs : patients, médecins, administrateurs
- Définition des cas d'utilisation
- Analyse des solutions existantes (aucune solution locale complète identifiée)

#### Phase 2 — Conception (Semaine 3-4)
- Modélisation de la base de données (10 tables, 3 vues, 2 procédures stockées)
- Conception de l'architecture technique (API REST + frontend statique)
- Maquettage des interfaces utilisateur
- Définition des routes API

#### Phase 3 — Développement (Semaine 5-10)
- Développement du backend (FastAPI, Python)
- Développement du frontend (HTML/CSS/JavaScript)
- Intégration et tests
- Corrections et optimisations

#### Phase 4 — Tests et finalisation (Semaine 11-12)
- Tests fonctionnels par rôle (patient, médecin, admin)
- Correction des bugs identifiés
- Documentation technique
- Déploiement local et démonstration

### Méthode de travail

- **Versioning** : Git + GitHub (https://github.com/BorutoNiang/sunu_kiray)
- **Environnement** : VS Code, Python 3.13, MySQL 8
- **Tests** : Tests manuels + validation via Swagger UI (http://localhost:8001/docs)

---

## 4. TECHNOLOGIES ET OUTILS UTILISÉS

### Backend

| Technologie | Version | Rôle |
|-------------|---------|------|
| Python | 3.13 | Langage principal du backend |
| FastAPI | 0.110+ | Framework API REST |
| uvicorn | 0.29+ | Serveur ASGI |
| pymysql | 1.1+ | Connecteur MySQL |
| python-jose | 3.3+ | Gestion des tokens JWT |
| bcrypt | 4.0+ | Hachage des mots de passe |
| python-dotenv | 1.0+ | Gestion des variables d'environnement |
| pydantic | 2.0+ | Validation des données |
| slowapi | 0.1.9+ | Rate limiting (protection brute force) |

### Frontend

| Technologie | Rôle |
|-------------|------|
| HTML5 | Structure des pages |
| CSS3 | Mise en forme et animations |
| JavaScript ES2022 | Logique frontend, appels API |
| Google Fonts (Syne, DM Sans) | Typographie |
| Chart.js 4.4 | Graphiques du dashboard |

### Base de données

| Technologie | Version | Rôle |
|-------------|---------|------|
| MySQL | 8.0+ | Système de gestion de base de données |
| Procédures stockées | — | Génération automatique des créneaux |
| Vues SQL | — | Requêtes complexes simplifiées |

### Outils de développement

| Outil | Usage |
|-------|-------|
| VS Code | Éditeur de code |
| Git / GitHub | Versioning et collaboration |
| Swagger UI | Documentation et test de l'API |
| MySQL Workbench | Administration de la base de données |

### Justification des choix techniques

**Pourquoi FastAPI ?**
FastAPI est un framework Python moderne, performant et auto-documenté. Il génère automatiquement une documentation Swagger interactive, ce qui facilite les tests et la collaboration. Sa validation automatique via Pydantic réduit les erreurs de données.

**Pourquoi JavaScript vanilla (sans framework) ?**
Pour un projet académique, éviter React ou Vue.js permet de se concentrer sur la logique métier sans surcharge de configuration. Le code est plus lisible et directement exécutable dans le navigateur.

**Pourquoi MySQL ?**
MySQL est largement utilisé dans les systèmes de santé africains, bien documenté et disponible sur tous les hébergeurs locaux. Les procédures stockées permettent d'encapsuler la logique de génération des créneaux directement en base.

**Pourquoi JWT ?**
Les JSON Web Tokens permettent une authentification stateless, adaptée à une API REST. Ils contiennent le rôle de l'utilisateur, ce qui permet un contrôle d'accès efficace sans requête base de données supplémentaire.

---

## 5. ARCHITECTURE DE LA SOLUTION

### Architecture générale

```
┌─────────────────────────────────────────────────────────┐
│                    NAVIGATEUR WEB                        │
│  ┌──────────┐  ┌───────────┐  ┌──────────┐  ┌────────┐ │
│  │auth.html │  │dashboard  │  │medecin   │  │patient │ │
│  │          │  │.html      │  │.html     │  │.html   │ │
│  └────┬─────┘  └─────┬─────┘  └────┬─────┘  └───┬────┘ │
│       └──────────────┴──────────────┴─────────────┘      │
│                         api.js                            │
│              (couche API centralisée + JWT)               │
└─────────────────────────────┬───────────────────────────┘
                              │ HTTP/JSON
                              ▼
┌─────────────────────────────────────────────────────────┐
│              BACKEND FastAPI (Python 3.13)               │
│                   http://localhost:8001                   │
│                                                          │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌───────────┐  │
│  │  /auth   │ │/medecins │ │/rendez-  │ │/dashboard │  │
│  │          │ │          │ │  vous    │ │           │  │
│  └──────────┘ └──────────┘ └──────────┘ └───────────┘  │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌───────────┐  │
│  │/structures│ │/alertes │ │/redeplois│ │  /admin   │  │
│  └──────────┘ └──────────┘ └──────────┘ └───────────┘  │
│                                                          │
│         security.py (JWT + bcrypt)                       │
│         database.py (connexion MySQL)                    │
└─────────────────────────────┬───────────────────────────┘
                              │ pymysql
                              ▼
┌─────────────────────────────────────────────────────────┐
│                    MySQL 8 — sunu_kiray                  │
│                                                          │
│  utilisateurs │ structures_sante │ medecins │ services   │
│  disponibilites │ rendez_vous │ alertes │ redeplois      │
│  notifications │ rapports │ horaires_medecins            │
│                                                          │
│  Vues : vue_charge_structures, vue_medecins_redeployables│
│  Procédures : generer_disponibilites(), verifier_charge()│
└─────────────────────────────────────────────────────────┘
```

### Structure des fichiers

```
sunu_kiray/
├── backend/
│   ├── routers/          ← 8 fichiers de routes API
│   ├── scripts/          ← Scripts SQL et utilitaires
│   ├── main.py           ← Point d'entrée FastAPI
│   ├── database.py       ← Connexion MySQL
│   ├── security.py       ← JWT + bcrypt
│   ├── utils.py          ← Fonctions utilitaires
│   └── requirements.txt
├── frontend/
│   ├── api.js            ← Couche API centralisée
│   ├── auth.html         ← Connexion / Inscription
│   ├── dashboard.html    ← Espace administrateur
│   ├── medecin.html      ← Espace médecin
│   ├── patient.html      ← Espace patient
│   └── index.html        ← Page d'accueil
├── database/
│   └── sunu_kiray.sql    ← Schéma complet
└── start.bat             ← Démarrage en un clic
```

---

## 6. CONCEPTION ET MODÉLISATION

### Modèle de données — 11 tables principales

| Table | Description | Champs clés |
|-------|-------------|-------------|
| `utilisateurs` | Tous les acteurs (patients, médecins, admins) | id, email, mot_de_passe (bcrypt), role |
| `structures_sante` | Hôpitaux et centres de santé | nom, type, capacite_journaliere, charge_actuelle |
| `medecins` | Profil étendu des médecins | specialite, disponibilite, peut_etre_redeploye |
| `services` | Spécialités par structure | nom, duree_consultation_mn, nb_medecins_requis |
| `horaires_medecins` | Emploi du temps récurrent | jour_semaine (0-5), heure_debut, heure_fin |
| `disponibilites` | Créneaux générés automatiquement | date_travail, nb_slots_max, nb_slots_pris |
| `rendez_vous` | Réservations patients | statut, code_confirmation, notes_medecin |
| `alertes` | Surcharges détectées | type_alerte, priorite (faible/moyenne/haute/critique) |
| `redeplois` | Missions temporaires | structure_origine, structure_destination, statut |
| `notifications` | Messages aux utilisateurs | type_notif, canal (sms/email/inapp) |
| `rapports` | Statistiques générées | type_rapport, donnees_json |

### Vues SQL

- **`vue_charge_structures`** : Calcule en temps réel le taux de charge (%) de chaque structure
- **`vue_medecins_redeployables`** : Liste les médecins disponibles pour une mission temporaire
- **`vue_rdv_aujourd_hui`** : Tous les rendez-vous du jour avec détails complets

### Procédures stockées

- **`generer_disponibilites(nb_jours)`** : Génère automatiquement les créneaux pour N jours à partir des horaires hebdomadaires
- **`verifier_charge_structure(id)`** : Déclenche une alerte si la charge dépasse le seuil configuré

### Flux d'authentification

```
Patient → POST /auth/login → Vérification bcrypt → JWT généré
JWT contient : { sub, role, nom, prenom, email, exp }
Toutes les requêtes protégées → Header: Authorization: Bearer <token>
```

### Flux de prise de rendez-vous

```
1. Patient sélectionne une structure
2. Patient sélectionne un service
3. Calendrier charge les dates disponibles (GET /rendez-vous/dates-disponibles)
4. Patient sélectionne une date → créneaux chargés (GET /rendez-vous/disponibilites)
5. Patient sélectionne un créneau et confirme
6. POST /rendez-vous → RDV créé avec statut "confirme" + code SMS
7. Médecin voit le RDV dans son planning
8. Jour J : médecin démarre (en_cours) → termine (termine + notes)
```

---

## 7. DÉVELOPPEMENT — FONCTIONNALITÉS RÉALISÉES

### Espace Patient

| Fonctionnalité | État | Description |
|----------------|------|-------------|
| Inscription | ✅ Réalisé | 3 étapes : rôle, identité, confirmation |
| Connexion | ✅ Réalisé | Email + mot de passe, redirection par rôle |
| Prise de RDV | ✅ Réalisé | Wizard 4 étapes avec calendrier dynamique |
| Créneaux en temps réel | ✅ Réalisé | Seuls les jours avec créneaux disponibles sont cliquables |
| Code de confirmation | ✅ Réalisé | Code 6 chiffres généré à la création |
| Mes rendez-vous | ✅ Réalisé | Liste avec statuts, annulation possible |
| Mon profil | ✅ Réalisé | Affichage et modification des informations |
| Mon dossier | ✅ Réalisé | Historique des consultations terminées |
| Notifications | ✅ Réalisé | Liste des RDV récents avec statuts |

### Espace Médecin

| Fonctionnalité | État | Description |
|----------------|------|-------------|
| Planning hebdomadaire | ✅ Réalisé | Calendrier dynamique avec vrais RDV de la BDD |
| Navigation semaines | ✅ Réalisé | Flèches précédent/suivant + bouton Aujourd'hui |
| Démarrer consultation | ✅ Réalisé | Bouton ▶ Démarrer → statut en_cours |
| Terminer consultation | ✅ Réalisé | Bouton ✓ Terminer + saisie notes médicales |
| Marquer absent | ✅ Réalisé | Bouton ✗ Absent pour les no-shows |
| Missions de redéploiement | ✅ Réalisé | Accepter/refuser les missions proposées |
| Mes disponibilités | ✅ Réalisé | Gestion des horaires récurrents (CRUD) |
| Toggle disponibilité | ✅ Réalisé | Bouton Disponible/Indisponible en temps réel |
| Mes statistiques | ✅ Réalisé | KPIs réels depuis la BDD (consultations, taux présence) |
| Mon profil | ✅ Réalisé | Affichage et modification |
| Notifications | ✅ Réalisé | RDV récents et à venir |

### Espace Administrateur

| Fonctionnalité | État | Description |
|----------------|------|-------------|
| Dashboard temps réel | ✅ Réalisé | KPIs : structures, médecins, RDV, alertes |
| Charge des structures | ✅ Réalisé | Barres de progression colorées (vert/orange/rouge) |
| Graphique activité | ✅ Réalisé | RDV des 7 derniers jours (Chart.js) |
| Gestion structures | ✅ Réalisé | Liste avec taux de charge et médecins disponibles |
| Gestion médecins | ✅ Réalisé | Liste avec filtres, statuts de disponibilité |
| Gestion RDV | ✅ Réalisé | Tous les RDV avec filtres (hôpital, date, statut) |
| Alertes | ✅ Réalisé | Liste des alertes actives, marquage comme traitée |
| Redéploiements | ✅ Réalisé | Formulaire de proposition + liste des missions |
| Rapports | ✅ Réalisé | Stats par structure, activité hebdomadaire |
| Génération créneaux | ✅ Réalisé | Bouton "🔄 Créneaux" → génère 30 jours automatiquement |

### API REST — 25 endpoints

| Méthode | Route | Accès |
|---------|-------|-------|
| POST | /auth/login | Public |
| POST | /auth/register | Public |
| GET/PUT | /auth/me | Connecté |
| GET | /structures | Connecté |
| GET | /structures/{id} | Connecté |
| GET | /medecins | Connecté |
| GET | /medecins/{id}/planning | Médecin/Admin |
| GET/POST/DELETE | /medecins/{id}/horaires | Médecin/Admin |
| PUT | /medecins/{id}/disponibilite | Médecin/Admin |
| GET | /rendez-vous | Connecté |
| POST | /rendez-vous | Patient |
| GET | /rendez-vous/disponibilites | Connecté |
| GET | /rendez-vous/dates-disponibles | Connecté |
| PUT | /rendez-vous/{id}/annuler | Patient/Admin |
| PUT | /rendez-vous/{id}/statut | Médecin/Admin |
| GET | /alertes | Admin |
| PUT | /alertes/{id}/traiter | Admin |
| GET/POST | /redeplois | Admin |
| PUT | /redeplois/{id}/repondre | Médecin |
| GET | /dashboard | Admin |
| POST | /admin/generer-creneaux | Admin |
| GET | /admin/stats-disponibilites | Admin |

---

## 8. TESTS ET VALIDATION

### Tests fonctionnels réalisés

| Scénario | Résultat |
|----------|----------|
| Inscription patient avec email existant | ✅ Erreur 409 retournée |
| Connexion avec mauvais mot de passe | ✅ Erreur 401 retournée |
| Prise de RDV sur créneau complet | ✅ Erreur 409 retournée |
| Double RDV même structure même jour | ✅ Erreur 409 retournée |
| Accès dashboard sans token | ✅ Redirection vers auth.html |
| Patient accédant à un RDV d'un autre patient | ✅ Erreur 403 retournée |
| Génération automatique des créneaux | ✅ 312 créneaux générés sur 30 jours |
| Nettoyage RDV passés au démarrage | ✅ Statut "absent" appliqué automatiquement |
| Rate limiting login (>10 req/min) | ✅ Erreur 429 retournée |

### Validation via Swagger UI

L'API est entièrement documentée et testable via `http://localhost:8001/docs`. Chaque endpoint est décrit avec ses paramètres, ses codes de retour et des exemples.

### Comptes de test

| Rôle | Email | Mot de passe |
|------|-------|--------------|
| Administrateur | admin@plateforme-med.sn | Sunu2025! |
| Médecin (Cardiologue) | a.diallo@med.sn | Sunu2025! |
| Médecin (Généraliste) | f.ndiaye@med.sn | Sunu2025! |
| Patient | m.sarr@gmail.com | Sunu2025! |

---

## 9. RÉSULTATS ET DÉMONSTRATION

### Résultats quantitatifs

- **6 structures de santé** configurées (Dakar, Thiès, Ziguinchor, Touba)
- **7 médecins** inscrits avec spécialités variées
- **13 services médicaux** disponibles
- **312 créneaux** générés automatiquement sur 30 jours
- **25 endpoints API** fonctionnels et documentés
- **5 pages web** complètes et responsives

### Indicateurs de performance

- Temps de réponse API moyen : **< 100ms** (local)
- Taille de la base de données : **~500 Ko** (données de test)
- Couverture fonctionnelle : **100%** des cas d'utilisation définis

### Lien de démonstration

```
URL : http://localhost:8001/app/auth.html
API : http://localhost:8001/docs
Code : https://github.com/BorutoNiang/sunu_kiray
```

---

## 10. DIFFICULTÉS RENCONTRÉES ET SOLUTIONS

| Difficulté | Solution apportée |
|------------|-------------------|
| **Compatibilité bcrypt** entre Node.js (génération) et Python (vérification) | Régénération des hash directement en Python via script `reset_passwords.py` |
| **Timedelta MySQL** sérialisé en secondes au lieu de HH:MM | Création d'une fonction utilitaire `fix_rows()` dans `utils.py` |
| **CORS bloqué** en mode `file://` | Servir le frontend via FastAPI (`StaticFiles`) sur la même origine |
| **JWT invalide** après redémarrage serveur | Correction : `sub` doit être une string dans le payload JWT |
| **Calendrier statique** ne reflétant pas les vrais RDV | Remplacement par un calendrier dynamique généré depuis l'API |
| **Duplication de code** dans `rendez_vous.py` | Réécriture complète du fichier avec une seule version propre |
| **Créneaux manquants** pour certaines structures | Ajout de médecins pour Pikine et Touba + génération automatique |

---

## 11. PERSPECTIVES D'AMÉLIORATION

### Court terme
- **Envoi SMS réel** via Twilio ou un opérateur local (Orange Sénégal, Free)
- **Notifications email** pour les rappels de RDV
- **Export PDF** des rapports statistiques

### Moyen terme
- **Application mobile** (React Native ou Flutter) pour une meilleure accessibilité
- **Carte interactive** des structures de santé (Leaflet + OpenStreetMap)
- **Système de notation** des médecins par les patients
- **Synchronisation temps réel** via WebSocket pour le dashboard admin

### Long terme
- **Déploiement cloud** sur un serveur sénégalais (hébergement local)
- **Intégration avec le système national de santé** (MSAS)
- **Intelligence artificielle** pour prédire les pics de demande
- **Téléconsultation** intégrée

---

## 12. CONCLUSION

Le projet **Sunu Kiray** ("Notre Santé" en Wolof) répond à un besoin réel et urgent du système de santé sénégalais. En développant une plateforme numérique complète permettant la prise de rendez-vous en ligne, la gestion des plannings médicaux et le redéploiement intelligent des ressources, ce projet démontre comment la technologie peut améliorer concrètement l'accès aux soins.

### Bilan technique

La solution est construite sur une architecture moderne et robuste :
- **Backend FastAPI** avec authentification JWT, validation des données, rate limiting et logging
- **Base de données MySQL** avec procédures stockées pour l'automatisation
- **Frontend responsive** en JavaScript vanilla, sans dépendance externe lourde
- **API REST documentée** avec 25 endpoints couvrant tous les cas d'utilisation

### Bilan fonctionnel

Les trois espaces utilisateurs (patient, médecin, administrateur) sont pleinement fonctionnels. Le flux complet — de la prise de rendez-vous par le patient jusqu'à la clôture de la consultation par le médecin — est opérationnel et testé.

### Valeur ajoutée

Ce projet va au-delà d'un simple exercice académique : il constitue une base solide pour un déploiement réel dans les structures de santé sénégalaises, avec une architecture extensible et une documentation complète.

---

*Rapport rédigé dans le cadre du Projet Personnel et Professionnel (PPP)*  
*DIC 1 / DGI / ESP / UCAD — Année 2025-2026*  
*Encadrant : Dr Mangoné FALL*
